# TÀI LIỆU ĐẶC TẢ KỸ THUẬT VÀ THIẾT KẾ SẢN PHẨM (SRS) - BẢN REVISED V1.1
## DỰ ÁN: CUSTOM CIRCULAR LED MATRIX SCREENSAVER (CusSSaver)

---

| **Thuộc tính** | **Nội dung** |
| :--- | :--- |
| **Dự án** | CusSSaver (Custom LED Matrix Screensaver) |
| **Vai trò** | Senior Product Manager & Tech Lead |
| **Khách hàng / Stakeholder** | The Boss |
| **Trạng thái** | Revised according to Boss Feedback - Pending Final Approval |
| **Phiên bản** | v1.1 (Cập nhật Dynamic Aspect Ratio & Wave Modulation) |
| **Ngày cập nhật** | 2026-11-10 |

---

## 1. TỔNG QUAN SẢN PHẨM (EXECUTIVE SUMMARY)

**CusSSaver** là ứng dụng Screensaver phong cách **Circular LED Matrix** (ma trận đèn LED tròn) cao cấp, được thiết kế chuyên biệt cho Windows theo triết lý:
1. **Hoàn toàn tàng hình khi Idle:** Nằm gọn gàng dưới System Tray, tiêu hao `CPU = 0.0%`, RAM tối thiểu, không ảnh hưởng đến bất kỳ tác vụ nào của hệ thống.
2. **Kích hoạt tức thì (On-Demand):** Một click chuột trái vào Tray icon là bung Fullscreen trên **toàn bộ các màn hình**.
3. **Chống ngủ Windows (Keep-Awake):** Duy trì màn hình sáng liên tục trong suốt thời gian screensaver chạy.
4. **Hiển thị thích ứng đa tỉ lệ (Smart Dynamic Fit):** Tự động nhận diện và tính toán khung hình cho bất kỳ tỷ lệ ảnh nào (`1:1`, `16:9`, `16:10`, `4:3`, `21:9`...):
   * **Nếu ảnh khớp tỷ lệ màn hình:** Tràn viền `100%`, **tuyệt đối không có bất kỳ dải đen nào**.
   * **Nếu ảnh lệch tỷ lệ màn hình:** Căn giữa giữ nguyên tỷ lệ (Aspect Fit) để ảnh không bị méo; phần viền thừa phủ dải lưới bóng LED ma trận ở trạng thái tắt đèn.
5. **Độ nét cao (Hi-Fi LED Matrix):** Đảm bảo visual (như bìa MJ *Invincible*) rõ từng chi tiết mắt, sống mũi, thần thái trên nền các bóng LED tròn có rãnh bezel vật lý.
6. **Cơ chế lướt sóng pha âm/dương (Asymmetric Wave Shimmer):**
   * **Pha sóng dương:** Bóng LED sáng chuẩn 100% màu gốc tự nhiên.
   * **Pha sóng âm:** Bóng LED chỉ hơi dịu lại (dimmed nhẹ ~70%), vẫn đảm bảo nhận rõ màu sắc và chi tiết của bóng LED, tạo cảm giác làn sóng quét êm dịu, không bị chớp giật hay tối đen.
7. **Thoát thông minh:** Rê chuột dứt khoát hoặc nhấn phím bất kỳ là thoát ngay và đưa CPU về 0.0%.

---

## 2. CHI TIẾT CẢI TIẾN THEO CHỈ ĐẠO CỦA SẾP

### 2.1 Thuật toán Auto-Fit đa tỉ lệ (Smart Aspect Auto-Fit Engine)
* **Nguyên tắc cốt lõi:**
  Gọi tỷ lệ màn hình hiển thị là:
  $$AR_{\text{screen}} = \frac{W_{\text{screen}}}{H_{\text{screen}}}$$
  Gọi tỷ lệ bức ảnh đầu vào là:
  $$AR_{\text{image}} = \frac{W_{\text{image}}}{H_{\text{image}}}$$
  Độ sai lệch tỷ lệ:
  $$\epsilon = |AR_{\text{screen}} - AR_{\text{image}}|$$

* **Trường hợp 1: Tỷ lệ ảnh khớp màn hình ($\epsilon \le 0.01$ - ví dụ ảnh 16:9 trên màn 16:9, hoặc ảnh 16:10 trên màn 16:10):**
  * **Hành vi:** Hệ thống ánh xạ ma trận LED phủ kín `100%` độ phân giải màn hình.
  * **Yêu cầu nghiêm ngặt:** **Tuyệt đối không để lại bất kỳ dải đen nào (Zero Black Bars)** ở 4 cạnh. Từng bóng LED ở góc rìa sát mép đều lấy đúng màu của ảnh gốc.
* **Trường hợp 2: Tỷ lệ ảnh khác màn hình ($\epsilon > 0.01$ - ví dụ ảnh 1:1 trên màn 16:9):**
  * **Hành vi:** Áp dụng thuật toán **Aspect Fit** (Uniform Scale). Bức ảnh được phóng to tối đa đến khi chạm mép trên/dưới (hoặc trái/phải), đặt chính giữa.
  * **Vùng biên dư:** Không để trống viền đen trơn, mà vẫn tiếp tục kéo dài cấu trúc lưới bóng LED tròn đồng nhất trên toàn màn hình, nhưng các bóng LED ở vùng này ở trạng thái tắt (`RGB = (0, 0, 0)` hoặc ambient `0.03`). Toàn bộ màn hình tạo thành một tấm panel LED liền mạch.

---

### 2.2 Giải thuật Sóng chéo: Điều chế Pha Dương / Pha Âm (Wave Modulation)
Theo đúng chỉ đạo của Sếp, shader không kéo tụt độ sáng xuống quá sâu hay làm biến màu bóng LED:

* **Công thức pha sóng chéo 45 độ:**
  Cho tọa độ bóng LED $(i, j)$ và thời gian $t$:
  $$\theta = \left(\frac{i + j}{\lambda} - \omega \cdot t\right) \pmod{2\pi}$$
  Biến thiên hình sin chuẩn:
  $$S = \sin(\theta) \quad \in [-1.0, 1.0]$$

* **Điều chế độ sáng theo pha:**
  * **Khi $S \ge 0$ (Pha sóng dương - Crest):**
    Bóng LED phát sáng ở mức độ chuẩn bình thường:
    $$\text{Factor} = 1.0 \quad (100\% \text{ Brightness - Màu sắc nguyên bản})$$
  * **Khi $S < 0$ (Pha sóng âm - Trough):**
    Bóng LED chỉ tối nhẹ một lượng có kiểm soát, áp dụng đường cong mượt:
    $$\text{Factor} = 1.0 - k_{\text{dim}} \cdot |S|$$
    *Với $k_{\text{dim}} \approx 0.28$ (tương đương độ sáng tối thiểu rơi vào khoảng $72\%$).*
  * **Màu xuất ra của bóng LED:**
    $$\vec{C}_{\text{final}} = \vec{C}_{\text{image}} \times \text{Factor}$$

* **Hiệu quả thị giác đạt được:**
  * Giữ trọn vẹn dải màu RGB và độ tương phản của ảnh (không bị bạc màu, không bị biến đổi hue).
  * Vùng sóng âm chỉ hơi lắng xuống nhẹ nhàng như một gợn sóng lướt qua mặt nước, người dùng vẫn nhìn rõ từng đường nét khuôn mặt của Michael Jackson tại vùng sóng âm.
  * Nhịp điệu quét mượt mà ở 60 FPS, mang lại cảm giác thư thái, cao cấp.

---

### 2.3 Giải thuật Lấy mẫu & Tạo khối LED Tròn (Circular LED Masking)
* **Kích thước ô lưới ($S$):** Tùy chỉnh qua cấu hình (ví dụ $8\text{px}$ hoặc $10\text{px}$).
* **Hình khối bóng LED:**
  * Trong mỗi ô $S \times S$, bóng tròn có bán kính $R = 0.42 \times S$.
  * Rìa bóng LED được khử răng cưa bằng hàm `smoothstep` trong khoảng $[R - 1.0\text{px}, R]$.
  * Lòng bóng LED có hiệu ứng nổi khối nhẹ (radial falloff ~10%) để giả lập mặt kính lồi của bóng đèn LED thực tế.
  * Khoảng cách giữa các bóng là rãnh bezel màu xám đen đậm `#0a0a0a`.

---

## 3. LUỒNG HOẠT ĐỘNG TOÀN DIỆN (SYSTEM WORKFLOW)

```text
[Khởi động PC] ──> [App nạp ngầm vào System Tray]
                         │
                         ├── CPU = 0.0%, RAM < 30MB
                         ├── Không can thiệp Windows Power
                         │
        ┌────────────────┴────────────────┐
        ▼                                 ▼
[Click chuột phải Tray]          [Click chuột trái Tray]
        │                                 │
  Mở Menu cài đặt:                        ▼
  • Bật Screensaver ngay         [Quét tất cả màn hình]
  • Chọn ảnh khác...                      │
  • Tùy chỉnh hạt LED (Mịn/Vừa/To)        ▼
  • Tùy chỉnh tốc độ sóng        [Mở Borderless Fullscreen trên từng màn hình]
  • Khởi động cùng Windows                │
  • Thoát                                 ▼
                                 [SetThreadExecutionState: Chống Sleep]
                                          │
                                          ▼
                                 [Render GLSL LED Matrix 60 FPS]
                                 • Auto-Fit tỉ lệ (Khớp = 100% tràn viền)
                                 • Sóng chéo: Dương = 100%, Âm = ~72%
                                          │
                                          ▼
                                 [Bắt sự kiện Chuột / Phím]
                                          │
                  ┌───────────────────────┴───────────────────────┐
                  ▼                                               ▼
         [Rung nhẹ < 15px]                             [Rê chuột mạnh HOẶC Bấm phím]
                  │                                               │
           Bỏ qua, tiếp tục chạy                                  ▼
                                                       [Đóng toàn bộ Fullscreen]
                                                                  │
                                                                  ▼
                                                       [Nhả quyền Power cho Windows]
                                                                  │
                                                                  ▼
                                                       [Quay về Tray, CPU = 0.0%]
```

---

## 4. MA TRẬN TÍNH NĂNG & TIÊU CHÍ NGHIỆM THU ĐÃ CẬP NHẬT

| Mã | Tính năng | Tiêu chuẩn nghiệm thu được Sếp phê duyệt |
| :---: | :--- | :--- |
| **AC-01** | **Khớp màn hình (Matching AR)** | Ảnh có tỷ lệ trùng với màn hình (ví dụ ảnh 16:9 trên màn 16:9) phải **phủ kín 100%, không xuất hiện bất kỳ dải đen nào**. |
| **AC-02** | **Lệch màn hình (Non-matching AR)** | Ảnh 1:1 hoặc khác tỷ lệ: Căn giữa tự nhiên, phần thừa hiển thị lưới bóng LED tắt đen đồng nhất với tổng thể. |
| **AC-03** | **Pha sóng dương** | Bóng LED đạt **100% độ sáng gốc**, hiển thị chuẩn xác màu sắc ảnh. |
| **AC-04** | **Pha sóng âm** | Bóng LED giảm độ sáng dịu xuống mức **~72%**, **tuyệt đối không bị tối đen hay mất màu**, chi tiết ảnh vẫn nhìn rõ nét. |
| **AC-05** | **Độ nét & Thẩm mỹ** | Mắt, mũi, môi của ảnh (như visual MJ Invincible) sắc sảo, nhận diện rõ chất liệu LED tròn, không bị biến dạng kỳ quặc. |
| **AC-06** | **CPU Idle ở Tray** | Đạt **0.0% CPU** khi thu dưới khay hệ thống. |
| **AC-07** | **Đa màn hình** | Phủ kín toàn bộ các màn hình đang kết nối khi click bật. |
| **AC-08** | **Ngăn Windows Sleep** | Giữ máy tính và màn hình luôn thức khi screensaver đang chạy. |
| **AC-09** | **Thoát nhạy & Chống rung** | Rung bàn nhẹ không tắt; rê chuột có chủ đích hoặc nhấn phím bất kỳ là tắt ngay lập tức. |
| **AC-10** | **Menu Tray tiện lợi** | Chuột phải có đầy đủ menu: Đổi ảnh, Đổi kích thước LED, Đổi tốc độ sóng, Khởi động cùng Windows, Thoát. |

---

## 5. THIẾT KẾ CẤU HÌNH MẪU (`settings.json`)

```json
{
  "image_path": "assets/custom.jpg",
  "led_size": 10,
  "led_spacing_ratio": 0.84,
  "wave_speed": 1.2,
  "wave_negative_dim": 0.28,
  "mouse_move_threshold": 15,
  "run_on_startup": false,
  "fps_target": 60
}
```
*Ghi chú kỹ thuật:* `wave_negative_dim: 0.28` tương đương độ sáng ở đáy sóng âm giữ vững ở mức $1.0 - 0.28 = 72\%$. Sếp có thể tinh chỉnh thông số này dễ dàng qua menu hoặc file config.
