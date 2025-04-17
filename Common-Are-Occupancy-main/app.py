import cv2
from ultralytics import YOLO

# YOLOv8 modeli
model = YOLO("yolov8s.pt")  # 'yolov8n.pt' yerine daha sağlam model

# Masa koordinatları (x1, y1, x2, y2)
tables = {
    "Table 11": (346, 300, 534, 612),
    "Table 12": (542, 300, 758, 614),
    "Table 21": (1042, 340, 1252, 610),
    "Table 22": (1250, 340, 1442, 610)
}

# Her karede masaları kontrol et
def check_occupancy(frame, results):
    occupancy = {}

    # 👇 Sadece bu etiketler işlenecek, diğerleri yok sayılacak
    allowed_labels = ['person', 'laptop', 'book', 'backpack', 'cell phone']

    for name, (x1, y1, x2, y2) in tables.items():
        is_occupied = False

        for result in results:
            boxes = result.boxes
            for box in boxes:
                cls_id = int(box.cls[0])
                label = model.model.names[cls_id]
                conf = float(box.conf[0])
                if conf < 0.3:
                    continue

                # ❌ Etiket istenmeyen bir nesneyse geç
                if label not in allowed_labels:
                    continue

                # 🟢 Geçerli nesne
                xA, yA, xB, yB = map(int, box.xyxy[0])
                center_x = (xA + xB) // 2
                center_y = (yA + yB) // 2

                # Çizimini yap
                cv2.rectangle(frame, (xA, yA), (xB, yB), (255, 255, 0), 2)
                cv2.putText(frame, label, (xA, yA - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)

                # Masa içinde mi kontrolü
                if x1 <= center_x <= x2 and y1 <= center_y <= y2:
                    is_occupied = True

        # Masa durumunu yaz ve çerçevele
        if is_occupied:
            color = (0, 0, 255)
            text = "Dolu"
        else:
            color = (0, 255, 0)
            text = "Boş"

        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
        cv2.putText(frame, f"{name}: {text}", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        occupancy[name] = text

    return frame, occupancy
# Video işleme fonksiyonu
def process_video(video_path):
    print("🎬 Video açılıyor:", video_path)
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        print("❌ Video açılamadı!")
        return

    print("✅ Video işleniyor... ESC ile çıkabilirsin.")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("⛔ Video bitti ya da kare alınamadı.")
            break

        results = model.track(frame, persist=True, verbose=False)
        frame, occupancy = check_occupancy(frame, results)

        # Konsola yaz
        print("---------- MASA DURUMLARI ----------")
        for table, status in occupancy.items():
            print(f"{table}: {status}")
        print("------------------------------------")

        cv2.imshow("Masa Takibi", frame)

        # ESC tuşu ile çık
        if cv2.waitKey(30) & 0xFF == 27:
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
     process_video(r"C:\Users\erenay\Desktop\Common-Are-Occupancy-main\Common-Are-Occupancy-main\library\video11.mp4")