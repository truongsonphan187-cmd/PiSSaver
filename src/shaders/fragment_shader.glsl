#version 330 core
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
    // Tọa độ pixel (gốc tọa độ 0,0 ở góc trên bên trái màn hình)
    vec2 frag_coord = vec2(gl_FragCoord.x, u_resolution.y - gl_FragCoord.y);

    // Tính tỉ lệ màn hình và tỉ lệ bức ảnh
    float screen_ar = u_resolution.x / u_resolution.y;
    float image_ar = u_image_size.x / u_image_size.y;
    
    vec2 draw_size;
    vec2 draw_offset;
    
    // Yêu cầu của Sếp: Nếu tỉ lệ khớp (hoặc gần khớp sai số < 2%), tràn 100% viền màn hình, KHÔNG ĐỂ LẠI DẢI ĐEN
    if (abs(screen_ar - image_ar) < 0.02) {
        draw_size = u_resolution;
        draw_offset = vec2(0.0, 0.0);
    } else if (screen_ar > image_ar) {
        // Màn hình rộng hơn ảnh (ví dụ màn 16:9, ảnh 1:1)
        draw_size = vec2(u_resolution.y * image_ar, u_resolution.y);
        draw_offset = vec2((u_resolution.x - draw_size.x) * 0.5, 0.0);
    } else {
        // Màn hình cao hơn ảnh (ví dụ màn dọc)
        draw_size = vec2(u_resolution.x, u_resolution.x / image_ar);
        draw_offset = vec2(0.0, (u_resolution.y - draw_size.y) * 0.5);
    }

    // Xác định ô ma trận LED
    vec2 cell_idx = floor(frag_coord / u_led_size);
    vec2 cell_center = (cell_idx + 0.5) * u_led_size;
    float radius = (u_led_size * 0.5) * u_spacing_ratio;
    float dist = length(frag_coord - cell_center);

    // Màu nền của khung bezel rãnh giữa các bóng LED
    vec3 bezel_color = vec3(0.035, 0.035, 0.04);

    // Kiểm tra xem ô LED có nằm trong vùng ảnh hay thuộc vùng rìa thừa
    bool is_outside = (cell_center.x < draw_offset.x || cell_center.x > draw_offset.x + draw_size.x ||
                       cell_center.y < draw_offset.y || cell_center.y > draw_offset.y + draw_size.y);

    vec3 base_color;
    if (is_outside) {
        // Vùng rìa ngoài: Vẫn là bóng LED ma trận nhưng ở trạng thái tắt đèn
        base_color = vec3(0.015, 0.015, 0.02);
    } else {
        vec2 uv = (cell_center - draw_offset) / draw_size;
        uv = clamp(uv, 0.0, 1.0);
        base_color = texture(u_texture, uv).rgb;
    }

    // Hiệu ứng sóng chéo 45 độ theo chỉ đạo của Sếp
    float wave_factor = 1.0;
    if (u_wave_speed > 0.001) {
        float wave_coord = cell_idx.x + cell_idx.y;
        float wavelength = 26.0; // Bước sóng tính theo số bóng LED
        float phase = (wave_coord / wavelength) * 6.2831853 - (u_time * u_wave_speed * 2.5);
        float s = sin(phase);
        
        // Pha sóng dương (s >= 0): 100% sáng chuẩn màu gốc
        // Pha sóng âm (s < 0): chỉ giảm nhẹ độ sáng (~72%), vẫn nhìn rõ nét màu sắc và chi tiết
        if (s < 0.0) {
            wave_factor = 1.0 - u_negative_dim * abs(s);
        }
    }

    // Hiệu ứng thấu kính tròn lồi 3D (Spherical Dome Lens)
    float norm_dist = clamp(dist / radius, 0.0, 1.0);
    float lens = 1.0 - 0.22 * norm_dist * norm_dist;
    
    // Ánh phản chiếu nhẹ ở góc trên-trái bóng LED
    vec2 glint_pos = cell_center - vec2(radius * 0.28, radius * 0.28);
    float glint_dist = length(frag_coord - glint_pos);
    float glint = exp(-glint_dist * glint_dist / (radius * 0.28 * radius * 0.28)) * 0.12;

    vec3 dot_color = (base_color * wave_factor * lens) + vec3(glint);

    // Khử răng cưa (Anti-aliasing) viền bóng tròn
    float edge = 1.0 - smoothstep(radius - 0.75, radius + 0.25, dist);

    // Hòa trộn giữa rãnh bezel đen và bóng LED
    vec3 final_color = mix(bezel_color, dot_color, edge);
    FragColor = vec4(final_color, 1.0);
}
