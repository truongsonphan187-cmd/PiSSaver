"""
Module quản lý cửa sổ Screensaver và Render Engine LED Matrix trên OpenGL.
Hỗ trợ hiển thị trên tất cả các màn hình, chống rung chuột và bắt sự kiện bàn phím.
"""

import os
import sys
import time
import math
import logging
from typing import List, Optional

from PyQt6.QtCore import Qt, QTimer, QPointF
from PyQt6.QtWidgets import QWidget, QApplication
from PyQt6.QtOpenGLWidgets import QOpenGLWidget
from PyQt6.QtGui import QScreen, QCursor
from OpenGL import GL
from PIL import Image

import numpy as np
from src.config import get_app_dir, resolve_image_path
from src import power


DEFAULT_VERTEX_SHADER = """#version 330 core
layout(location = 0) in vec2 aPos;
void main() {
    gl_Position = vec4(aPos, 0.0, 1.0);
}
"""

DEFAULT_FRAGMENT_SHADER = """#version 330 core
out vec4 FragColor;

uniform vec2 u_resolution;
uniform vec2 u_image_size;
uniform sampler2D u_texture;
uniform float u_time;
uniform float u_led_size;
uniform float u_spacing_ratio;
uniform float u_wave_speed;
uniform float u_negative_dim;

void main() {
    vec2 frag_coord = vec2(gl_FragCoord.x, u_resolution.y - gl_FragCoord.y);

    float screen_ar = u_resolution.x / u_resolution.y;
    float image_ar = u_image_size.x / u_image_size.y;
    
    vec2 draw_size;
    vec2 draw_offset;
    
    if (abs(screen_ar - image_ar) < 0.02) {
        draw_size = u_resolution;
        draw_offset = vec2(0.0, 0.0);
    } else if (screen_ar > image_ar) {
        draw_size = vec2(u_resolution.y * image_ar, u_resolution.y);
        draw_offset = vec2((u_resolution.x - draw_size.x) * 0.5, 0.0);
    } else {
        draw_size = vec2(u_resolution.x, u_resolution.x / image_ar);
        draw_offset = vec2(0.0, (u_resolution.y - draw_size.y) * 0.5);
    }

    vec2 cell_idx = floor(frag_coord / u_led_size);
    vec2 cell_center = (cell_idx + 0.5) * u_led_size;
    float radius = (u_led_size * 0.5) * u_spacing_ratio;
    float dist = length(frag_coord - cell_center);

    vec3 bezel_color = vec3(0.035, 0.035, 0.04);

    bool is_outside = (cell_center.x < draw_offset.x || cell_center.x > draw_offset.x + draw_size.x ||
                       cell_center.y < draw_offset.y || cell_center.y > draw_offset.y + draw_size.y);

    vec3 base_color;
    if (is_outside) {
        base_color = vec3(0.015, 0.015, 0.02);
    } else {
        vec2 uv = (cell_center - draw_offset) / draw_size;
        uv = clamp(uv, 0.0, 1.0);
        base_color = texture(u_texture, uv).rgb;
    }

    float wave_factor = 1.0;
    if (u_wave_speed > 0.001) {
        float wave_coord = cell_idx.x + cell_idx.y;
        float wavelength = 26.0;
        float phase = (wave_coord / wavelength) * 6.2831853 - (u_time * u_wave_speed * 2.5);
        float s = sin(phase);
        
        if (s < 0.0) {
            wave_factor = 1.0 - u_negative_dim * abs(s);
        }
    }

    float norm_dist = clamp(dist / radius, 0.0, 1.0);
    float lens = 1.0 - 0.22 * norm_dist * norm_dist;
    
    vec2 glint_pos = cell_center - vec2(radius * 0.28, radius * 0.28);
    float glint_dist = length(frag_coord - glint_pos);
    float glint = exp(-glint_dist * glint_dist / (radius * 0.28 * radius * 0.28)) * 0.12;

    vec3 dot_color = (base_color * wave_factor * lens) + vec3(glint);
    float edge = 1.0 - smoothstep(radius - 0.75, radius + 0.25, dist);

    vec3 final_color = mix(bezel_color, dot_color, edge);
    FragColor = vec4(final_color, 1.0);
}
"""


def load_shader_source(filename: str) -> str:
    """Tải nội dung mã nguồn shader với fallback an toàn tuyệt đối."""
    base_dir = getattr(sys, '_MEIPASS', os.path.dirname(__file__))
    candidates = [
        os.path.join(base_dir, "shaders", filename),
        os.path.join(base_dir, "src", "shaders", filename),
        os.path.join(get_app_dir(), "src", "shaders", filename),
        os.path.join(os.path.dirname(__file__), "shaders", filename),
    ]
    for p in candidates:
        if os.path.exists(p):
            try:
                with open(p, "r", encoding="utf-8") as f:
                    return f.read()
            except Exception:
                pass
    
    # Fallback trực tiếp nếu không tìm thấy file trên đĩa
    if "vertex" in filename.lower():
        return DEFAULT_VERTEX_SHADER
    return DEFAULT_FRAGMENT_SHADER


class LEDMatrixWidget(QOpenGLWidget):
    """OpenGL Widget chuyên biệt vẽ Circular LED Matrix kết hợp Shimmer Wave."""

    def __init__(self, config: dict, parent=None):
        super().__init__(parent)
        self.config = config
        self.start_time = time.perf_counter()
        
        # Biến OpenGL
        self.shader_program = 0
        self.texture_id = 0
        self.vao = 0
        self.vbo = 0
        self.image_size = (1920, 1080)
        
        # Timer cập nhật 60 FPS
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)
        target_fps = self.config.get("fps_target", 60)
        interval_ms = max(1, int(1000 / target_fps))
        self.timer.start(interval_ms)

    def initializeGL(self):
        GL.glClearColor(0.02, 0.02, 0.025, 1.0)
        
        # 1. Biên dịch Shaders
        v_src = load_shader_source("vertex_shader.glsl")
        f_src = load_shader_source("fragment_shader.glsl")
        
        vs = GL.glCreateShader(GL.GL_VERTEX_SHADER)
        GL.glShaderSource(vs, v_src)
        GL.glCompileShader(vs)
        if not GL.glGetShaderiv(vs, GL.GL_COMPILE_STATUS):
            err = GL.glGetShaderInfoLog(vs).decode()
            logging.error(f"Lỗi biên dịch Vertex Shader: {err}")

        fs = GL.glCreateShader(GL.GL_FRAGMENT_SHADER)
        GL.glShaderSource(fs, f_src)
        GL.glCompileShader(fs)
        if not GL.glGetShaderiv(fs, GL.GL_COMPILE_STATUS):
            err = GL.glGetShaderInfoLog(fs).decode()
            logging.error(f"Lỗi biên dịch Fragment Shader: {err}")

        self.shader_program = GL.glCreateProgram()
        GL.glAttachShader(self.shader_program, vs)
        GL.glAttachShader(self.shader_program, fs)
        GL.glLinkProgram(self.shader_program)
        if not GL.glGetProgramiv(self.shader_program, GL.GL_LINK_STATUS):
            err = GL.glGetProgramInfoLog(self.shader_program).decode()
            logging.error(f"Lỗi liên kết Shader Program: {err}")

        GL.glDeleteShader(vs)
        GL.glDeleteShader(fs)

        # 2. Tạo Fullscreen Quad (Hình chữ nhật phủ toàn màn hình)
        quad_vertices = np.array([
            -1.0, -1.0,
             1.0, -1.0,
            -1.0,  1.0,
            -1.0,  1.0,
             1.0, -1.0,
             1.0,  1.0,
        ], dtype=np.float32)

        self.vao = GL.glGenVertexArrays(1)
        self.vbo = GL.glGenBuffers(1)

        GL.glBindVertexArray(self.vao)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.vbo)
        GL.glBufferData(GL.GL_ARRAY_BUFFER, quad_vertices.nbytes, quad_vertices, GL.GL_STATIC_DRAW)

        GL.glEnableVertexAttribArray(0)
        GL.glVertexAttribPointer(0, 2, GL.GL_FLOAT, GL.GL_FALSE, 2 * 4, None)
        GL.glBindVertexArray(0)

        # 3. Nạp ảnh Texture
        self.load_image_texture()

    def load_image_texture(self):
        img_path = resolve_image_path(self.config.get("image_path", "assets/custom.jpg"))
        if not os.path.exists(img_path):
            logging.warning(f"Không tìm thấy ảnh tại {img_path}, tạo ảnh fallback...")
            # Tạo ảnh mẫu đen trắng tạm
            img = Image.new("RGB", (1024, 1024), color=(230, 230, 230))
        else:
            try:
                img = Image.open(img_path).convert("RGB")
            except Exception as e:
                logging.error(f"Không thể đọc file ảnh {img_path}: {e}")
                img = Image.new("RGB", (1024, 1024), color=(20, 20, 20))

        self.image_size = img.size
        img_data = img.tobytes()

        if self.texture_id == 0:
            self.texture_id = GL.glGenTextures(1)

        GL.glBindTexture(GL.GL_TEXTURE_2D, self.texture_id)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_S, GL.GL_CLAMP_TO_EDGE)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_T, GL.GL_CLAMP_TO_EDGE)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MIN_FILTER, GL.GL_LINEAR_MIPMAP_LINEAR)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MAG_FILTER, GL.GL_LINEAR)

        GL.glTexImage2D(
            GL.GL_TEXTURE_2D, 0, GL.GL_RGB,
            img.width, img.height, 0,
            GL.GL_RGB, GL.GL_UNSIGNED_BYTE, img_data
        )
        GL.glGenerateMipmap(GL.GL_TEXTURE_2D)
        GL.glBindTexture(GL.GL_TEXTURE_2D, 0)
        logging.info(f"Đã nạp texture ảnh thành công: {img.width}x{img.height}")

    def resizeGL(self, w: int, h: int):
        dpr = self.devicePixelRatio()
        GL.glViewport(0, 0, int(w * dpr), int(h * dpr))

    def paintGL(self):
        GL.glClear(GL.GL_COLOR_BUFFER_BIT)
        if self.shader_program == 0:
            return

        GL.glUseProgram(self.shader_program)

        # Tính toán độ phân giải vật lý thực tế trên màn hình (High-DPI aware)
        dpr = self.devicePixelRatio()
        real_w = float(self.width() * dpr)
        real_h = float(self.height() * dpr)
        elapsed = float(time.perf_counter() - self.start_time)

        # Truyền Uniforms vào GLSL
        loc_res = GL.glGetUniformLocation(self.shader_program, "u_resolution")
        GL.glUniform2f(loc_res, real_w, real_h)

        loc_img = GL.glGetUniformLocation(self.shader_program, "u_image_size")
        GL.glUniform2f(loc_img, float(self.image_size[0]), float(self.image_size[1]))

        loc_time = GL.glGetUniformLocation(self.shader_program, "u_time")
        GL.glUniform1f(loc_time, elapsed)

        # Kích thước LED scale theo tỉ lệ điểm ảnh vật lý
        led_size = float(self.config.get("led_size", 10)) * dpr
        loc_led = GL.glGetUniformLocation(self.shader_program, "u_led_size")
        GL.glUniform1f(loc_led, led_size)

        loc_spacing = GL.glGetUniformLocation(self.shader_program, "u_spacing_ratio")
        GL.glUniform1f(loc_spacing, float(self.config.get("led_spacing_ratio", 0.84)))

        loc_wave = GL.glGetUniformLocation(self.shader_program, "u_wave_speed")
        GL.glUniform1f(loc_wave, float(self.config.get("wave_speed", 1.2)))

        loc_dim = GL.glGetUniformLocation(self.shader_program, "u_negative_dim")
        GL.glUniform1f(loc_dim, float(self.config.get("wave_negative_dim", 0.28)))

        # Kích hoạt Texture
        GL.glActiveTexture(GL.GL_TEXTURE0)
        GL.glBindTexture(GL.GL_TEXTURE_2D, self.texture_id)
        loc_tex = GL.glGetUniformLocation(self.shader_program, "u_texture")
        GL.glUniform1i(loc_tex, 0)

        # Vẽ Fullscreen Quad
        GL.glBindVertexArray(self.vao)
        GL.glDrawArrays(GL.GL_TRIANGLES, 0, 6)
        GL.glBindVertexArray(0)
        GL.glUseProgram(0)

    def closeEvent(self, event):
        self.timer.stop()
        super().closeEvent(event)


class ScreensaverWindow(QWidget):
    """Cửa sổ Fullscreen không viền hiển thị trên một màn hình chỉ định."""

    def __init__(self, screen: QScreen, config: dict, dismiss_callback):
        super().__init__()
        self.screen_obj = screen
        self.config = config
        self.dismiss_callback = dismiss_callback
        
        self.initial_mouse_pos: Optional[QPointF] = None
        self.threshold = float(self.config.get("mouse_move_threshold", 15))

        # Thiết lập cửa sổ Fullscreen không viền, TopMost
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.SubWindow
        )
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, False)
        
        # Ẩn con trỏ chuột
        self.setCursor(Qt.CursorShape.BlankCursor)
        self.setMouseTracking(True)

        # Khởi tạo widget render OpenGL
        self.gl_widget = LEDMatrixWidget(config, self)

    def show_on_screen(self):
        geo = self.screen_obj.geometry()
        self.setGeometry(geo)
        self.gl_widget.setGeometry(0, 0, geo.width(), geo.height())
        self.show()
        self.raise_()
        self.activateWindow()

    def mouseMoveEvent(self, event):
        pos = event.globalPosition()
        if self.initial_mouse_pos is None:
            self.initial_mouse_pos = pos
            return
        
        # Tính khoảng cách di chuyển để lọc rung bàn
        dx = pos.x() - self.initial_mouse_pos.x()
        dy = pos.y() - self.initial_mouse_pos.y()
        dist = math.sqrt(dx * dx + dy * dy)
        
        if dist > self.threshold:
            logging.info(f"Phát hiện di chuyển chuột ({dist:.1f}px > {self.threshold}px) -> Thoát screensaver.")
            self.dismiss_callback()

    def mousePressEvent(self, event):
        logging.info("Phát hiện click chuột -> Thoát screensaver.")
        self.dismiss_callback()

    def keyPressEvent(self, event):
        logging.info(f"Phát hiện nhấn phím ({event.key()}) -> Thoát screensaver.")
        self.dismiss_callback()

    def wheelEvent(self, event):
        logging.info("Phát hiện cuộn chuột -> Thoát screensaver.")
        self.dismiss_callback()


class ScreensaverManager:
    """Quản lý các cửa sổ Screensaver trên tất cả các màn hình."""

    def __init__(self, config: dict):
        self.config = config
        self.windows: List[ScreensaverWindow] = []
        self.is_active = False

    def start(self):
        if self.is_active:
            return
        
        logging.info("Đang kích hoạt Screensaver trên tất cả màn hình...")
        self.is_active = True
        
        # Chống tắt màn hình / Sleep
        power.prevent_sleep()
        
        # Quét và phủ kín tất cả màn hình
        screens = QApplication.screens()
        self.windows = []
        for screen in screens:
            win = ScreensaverWindow(screen, self.config, self.stop)
            self.windows.append(win)
            win.show_on_screen()

    def stop(self):
        if not self.is_active:
            return
        
        logging.info("Đang đóng Screensaver và nhả tài nguyên...")
        self.is_active = False
        
        for win in self.windows:
            try:
                win.close()
            except Exception as e:
                logging.error(f"Lỗi khi đóng window: {e}")
        self.windows.clear()
        
        # Trả lại quyền Sleep cho Windows
        power.allow_sleep()
        
        # Khôi phục con trỏ chuột
        QApplication.restoreOverrideCursor()
        logging.info("Screensaver đã đóng hoàn toàn, ứng dụng về chế độ ngủ sâu.")
