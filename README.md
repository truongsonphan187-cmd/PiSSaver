# CusSSaver - Custom Circular LED Matrix Screensaver

> **Ứng dụng Screensaver ma trận LED tròn dành riêng cho Windows.**  
> Tối ưu hiệu năng tuyệt đối: **0.0% CPU khi ẩn khay hệ thống**, bung Fullscreen tức thì trên tất cả màn hình, ngăn Windows Sleep và hiệu ứng lướt sóng chéo nghệ thuật.

---

## 🌟 TÍNH NĂNG NỔI BẬT

1. **Ngủ sâu ở Khay hệ thống (Stealth Mode - 0.0% CPU):**
   * Khi không sử dụng, ứng dụng chỉ hiển thị một biểu tượng nhỏ gọn dưới góc phải màn hình (System Tray).
   * Đóng băng hoàn toàn vòng lặp render, không chiếm dụng CPU, RAM tĩnh cực thấp (< 30MB).
2. **Kích hoạt tức thì (On-Demand Activation):**
   * Nhấp chuột trái vào biểu tượng Tray -> Screensaver ngay lập tức bung Fullscreen trên **toàn bộ các màn hình**.
3. **Chống tắt màn hình / Sleep (Windows Keep-Awake):**
   * Sử dụng Windows API `SetThreadExecutionState` để ngăn hệ thống tắt màn hình hoặc rơi vào chế độ Sleep khi đang chạy screensaver.
4. **Thuật toán Smart Auto-Fit (Thích ứng mọi tỷ lệ ảnh):**
   * **Khi ảnh khớp tỷ lệ màn hình (ví dụ 16:9 trên màn 16:9):** Tự động tràn viền `100%`, **tuyệt đối không để lại bất kỳ dải đen nào**.
   * **Khi ảnh lệch tỷ lệ (ví dụ ảnh vuông 1:1 bìa album MJ Invincible trên màn 16:9):** Tự động căn giữa chuẩn tỷ lệ; các vùng trống xung quanh tiếp tục được phủ lưới bóng LED ma trận ở trạng thái tắt đèn đồng nhất.
5. **Hi-Fi Circular LED & Điều chế Sóng chéo (Wave Shimmer):**
   * Mỗi bóng LED tròn được dựng khối 3D mềm mại, có rãnh bezel vật lý và khử răng cưa mượt mà.
   * **Pha sóng dương:** Bóng LED sáng chuẩn 100% màu sắc gốc.
   * **Pha sóng âm:** Bóng LED chỉ dịu nhẹ xuống (~72%), vẫn nhìn rõ nét toàn bộ chi tiết khuôn mặt và màu sắc.
   * Chạy hoàn toàn trên GPU bằng OpenGL GLSL Shader ở tần số 60 FPS.
6. **Thoát thông minh & Chống rung bàn:**
   * Di chuyển chuột dứt khoát hoặc bấm phím bất kỳ để tắt screensaver ngay lập tức và đưa CPU về 0.0%.
   * Tích hợp bộ lọc rung chấn: va chạm nhẹ vào bàn khiến chuột dịch chuyển < 15 pixel sẽ không bị tắt nhầm.

---

## 🚀 HƯỚNG DẪN SỬ DỤNG NHANH

### Cách 1: Chạy trực tiếp file Release (.exe)
Vào thư mục `dist\` và khởi chạy:
```text
dist\CusSSaver.exe
```
* Ứng dụng sẽ xuất hiện ngay dưới Khay hệ thống (System Tray).
* **Click chuột trái** vào icon để bật Screensaver ngay.
* **Click chuột phải** vào icon để mở Menu cài đặt.

### Cách 2: Tự build lại file .exe
Chạy file script:
```text
build_exe.bat
```
File thực thi mới sẽ được xuất ra tại `dist\CusSSaver.exe`.

---

## 🖼️ HƯỚNG DẪN THAY ĐỔI ẢNH NỀN

* **Cách 1 (Nhanh nhất qua giao diện):**
  1. Click chuột phải vào biểu tượng CusSSaver ở khay hệ thống.
  2. Chọn **"🖼️ Chọn ảnh nguồn..."**.
  3. Chọn bất kỳ bức ảnh nào (`.jpg`, `.png`, `.webp`, `.bmp`). Cài đặt sẽ được lưu tự động.
* **Cách 2 (Copy đè file):**
  1. Click chuột phải vào icon -> Chọn **"📁 Mở thư mục ảnh"**.
  2. Dán đè bức ảnh bạn muốn dùng và đổi tên thành `custom.jpg`.

---

## ⚙️ MENU ĐIỀU KHIỂN DƯỚI SYSTEM TRAY

Khi click chuột phải vào icon ở khay hệ thống:
* 🚀 **Bật Screensaver ngay:** Kích hoạt toàn màn hình.
* 🖼️ **Chọn ảnh nguồn...:** Chọn ảnh từ máy tính.
* ⚙️ **Kích thước bóng LED:**
  * *Rất mịn (Fine - 6px):* Dành cho ảnh chi tiết cao.
  * *Vừa vặn (Medium - 10px):* Cân bằng hoàn hảo giữa chất LED và độ sắc nét.
  * *Hạt to (Coarse - 16px):* Phong cách Retro Pixel Art.
* 🌊 **Tốc độ sóng lướt:**
  * *Tắt sóng (Tĩnh)*
  * *Chậm & Dịu (Slow - 0.8)*
  * *Tiêu chuẩn (Normal - 1.2)*
  * *Nhanh (Fast - 2.0)*
* 📁 **Mở thư mục ảnh:** Mở nhanh thư mục chứa `custom.jpg`.
* 🔄 **Khởi động cùng Windows:** Tự động chạy ngầm khi mở máy.
* ❌ **Thoát hoàn toàn:** Đóng ứng dụng và giải phóng tài nguyên.

---

## 🛠️ CẤU TRÚC MÃ NGUỒN

```text
CusSSaver/
├── assets/                     # Tài nguyên ảnh mặc định & icon
│   ├── custom.jpg              # Ảnh mẫu phong cách MJ Invincible
│   └── icon.ico                # Icon khay hệ thống
├── dist/                       # Bản phát hành chạy độc lập
│   ├── CusSSaver.exe           # File chạy chính thức cho người dùng
│   ├── assets/                 # Thư mục ảnh đi kèm file .exe
│   └── settings.json           # File cấu hình
├── src/
│   ├── main.py                 # Điểm khởi động & Single instance mutex
│   ├── config.py               # Quản lý cấu hình & Registry Startup
│   ├── tray.py                 # Quản lý System Tray & Context Menu
│   ├── power.py                # Wrapper Win32 API chống Windows Sleep
│   ├── screensaver_window.py   # Cửa sổ Fullscreen đa màn hình & Bộ render OpenGL
│   └── shaders/
│       ├── vertex_shader.glsl  # Vertex Shader GLSL
│       └── fragment_shader.glsl# Fragment Shader render bóng LED & sóng chéo
├── build_exe.bat               # Script đóng gói ra file .exe 1-click
├── requirements.txt            # Danh sách thư viện Python
├── settings.json               # Cấu hình mặc định
├── SPECIFICATION.md            # Tài liệu đặc tả kỹ thuật chi tiết v1.1
└── README.md                   # Tài liệu hướng dẫn sử dụng
```
