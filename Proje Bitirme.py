import cv2

# Gerekli kütüphaneleri içe aktar, eğer yüklü değilse model devre dışı bırakılır.
try:
    import torch
    from ultralytics import YOLO
except ModuleNotFoundError:
    print("'torch' and 'ultralytics' modules are required but not installed. YOLO-based detection will be disabled.")
    YOLO = None

def process_frame(frame, model):
    """
    Her karede, YOLO modeliyle 'person', 'book' ve 'table' nesnelerini tespit eder.
    Tespit edilen nesneler, belirlenen renklerle (insan: yeşil, kitap: mavi, masa: kırmızı) kare içine alınır ve etiketleri ekrana yazdırılır.
    """
    # Model kullanılabilir değilse, işlem yapılmadan görüntü döndürülür.
    if model is None:
        print("Model is not available!")
        return frame

    # Modeli kullanarak nesne tespiti yap.
    results = model(frame)
    print(f"Number of detections: {len(results[0].boxes)}")

    # kisi sayisi alma  değişkeni
    person_count = 0
    
    # Her bir tespit sonucunu işleme al.
    for result in results:
        for box in result.boxes:
            # Kare koordinatlarını al ve tam sayıya çevir.
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            # Sınıf etiketini al.
            label = result.names[int(box.cls[0])]
            print(f"Detected: {label}")

            # sandalye,masa,kitap,insan tespit etme.
            if label.lower() in ['person', 'book', 'table', 'chair']:
                if label.lower() == 'person':
                    color = (0, 255, 0)    # Yeşil: insan
                    person_count += 1
                elif label.lower() == 'book':
                    color = (255, 0, 0)    # Mavi: kitap
                elif label.lower() == 'table':
                    color = (0, 0, 255)    # Kırmızı: masa
                elif label.lower() == 'chair':
                    color = (255, 255, 0)  # Turkuaz: sandalye
                else:
                    color = (255, 255, 255)
                
                # Kare içine alma ve etiketi ekrana yazdırma.
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

    # kisi sayısını ekrana yazdırma.
    height, width = frame.shape[:2]
    count_text = f"People: {person_count}"
    text_size = cv2.getTextSize(count_text, cv2.FONT_HERSHEY_SIMPLEX, 1, 2)[0]
    text_x = width - text_size[0] - 10
    text_y = height - 20
    cv2.putText(frame, count_text, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

    return frame

def main(video_path):
    # Video dosyasını aç.
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Error: Could not open video file at {video_path}")
        return
        
    # YOLO modelini yükle, eğer modül mevcutsa.
    model = YOLO("yolov8n.pt") if YOLO else None
    if model is None:
        print("YOLO model calismadi!")
    else:
        print("YOLO model calisti!")

    # Video boyutlarını al
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    # Pencereyi oluştur ve boyutlandır
    cv2.namedWindow("Kütüphane Masa Takip", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Kütüphane Masa Takip", frame_width, frame_height)

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            print("Error: Could not read frame")
            break

        # Her kareyi işleme al.
        processed_frame = process_frame(frame, model)
        
        # İşlenmiş kareyi anlık olarak ekranda göster.
        cv2.imshow("Kütüphane Masa Takip", processed_frame)
        

    # Kaynakları serbest bırak ve pencereleri kapat.
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    video_path = r"C:\Users\Mustafa\Desktop\Yeni klasör\camera1.mp4"  # Yolu kontrol edin
    main(video_path)
    # Create a Flask web server for the mobile interface
    from flask import Flask, render_template, jsonify
    import threading

    app = Flask(__name__)

    # Store table status
    tables = {
        1: {"occupied": False, "people": 0},
        2: {"occupied": False, "people": 0}, 
        3: {"occupied": False, "people": 0},
        4: {"occupied": False, "people": 0},
        5: {"occupied": False, "people": 0},
        6: {"occupied": False, "people": 0}
    }

    @app.route('/')
    def index():
        return render_template('index.html', tables=tables)

    @app.route('/api/tables')
    def get_tables():
        return jsonify(tables)

    def update_table_status(table_id, occupied, people):
        tables[table_id]["occupied"] = occupied
        tables[table_id]["people"] = people

    def run_flask():
        app.run(host='0.0.0.0', port=5000)

    # Start Flask server in a separate thread
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()

    # Create templates/index.html with this content:
    """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Library Table Status</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            .table-grid {
                display: grid;
                grid-template-columns: repeat(2, 1fr);
                gap: 20px;
                padding: 20px;
            }
            .table {
                background: #fff;
                border: 2px solid #ddd;
                border-radius: 8px;
                padding: 20px;
                text-align: center;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            .table.occupied {
                background: #ffebee;
            }
            .table-number {
                font-size: 24px;
                font-weight: bold;
            }
            .people-count {
                margin-top: 10px;
                color: #666;
            }
        </style>
    </head>
    <body>
        <div class="table-grid">
            {% for id, table in tables.items() %}
            <div class="table {% if table.occupied %}occupied{% endif %}">
                <div class="table-number">Table {{ id }}</div>
                <div class="people-count">People: {{ table.people }}</div>
            </div>
            {% endfor %}
        </div>
        <script>
            function updateTables() {
                fetch('/api/tables')
                    .then(response => response.json())
                    .then(data => {
                        for (let id in data) {
                            let table = document.querySelector(`.table:nth-child(${id})`);
                            table.classList.toggle('occupied', data[id].occupied);
                            table.querySelector('.people-count').textContent = `People: ${data[id].people}`;
                        }
                    });
            }
            setInterval(updateTables, 1000);
        </script>
    </body>
    </html>
    """
