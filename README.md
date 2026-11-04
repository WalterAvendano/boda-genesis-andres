# 💍 Aplicativo Boda QR & Google Drive

Aplicativo web ligero y elegante para que los invitados a una boda o evento escaneen un código QR desde las mesas y suban fácilmente sus fotos y videos directamente a una carpeta compartida de Google Drive (sin necesidad de tener cuenta de Google ni iniciar sesión).

---

## 🚀 Inicio Rápido en Local

Puedes probar la aplicación en tu computadora de inmediato:

1. **Doble clic en:** `iniciar.bat`
   *(O ejecuta en la terminal dentro de esta carpeta: `.\venv\Scripts\python.exe app.py`)*

2. Abre en tu navegador:
   - **Vista para invitados:** [http://localhost:5000](http://localhost:5000)
   - **Diseñador e impresor de tarjeta QR para mesas:** [http://localhost:5000/qr](http://localhost:5000/qr)

> **Modo Demo Activo:** Si aún no has conectado Google Drive, la app funciona 100% en modo local guardando las fotos de prueba en la carpeta `uploads/`.

---

## 📁 Estructura del Proyecto

```text
boda-qr-drive/
├── app.py                 # Servidor Flask principal y API
├── drive_service.py       # Conexión con Google Drive API y subida de archivos
├── generate_qr.py         # Generador de alta resolución de tarjetas QR de boda
├── iniciar.bat            # Acceso directo para ejecutar en Windows con 1 clic
├── templates/
│   ├── index.html         # Pantalla móvil elegante para invitados
│   └── qr.html            # Diseñador interactivo e impresor de tarjetas de mesa
├── uploads/               # Carpeta local para fotos/videos (modo demo o respaldo)
├── .env                   # Configuración (Nombres de novios, ID de Drive, etc.)
├── vercel.json            # Configuración para despliegue gratuito en Vercel
└── requirements.txt       # Librerías de Python
```

---

## ☁️ Conexión con Google Drive (5 minutos)

Para que los archivos suban automáticamente a tu cuenta de Google Drive:

### 1. Crear la carpeta en Google Drive
1. Ve a [Google Drive](https://drive.google.com).
2. Crea una carpeta (por ejemplo: `Fotos Boda Ana y Carlos`).
3. Abre la carpeta y copia el **ID de la carpeta** desde la barra de direcciones:
   - `https://drive.google.com/drive/folders/`**`1a2B3c4D5e6F7g...`** *(Este código es tu `DRIVE_FOLDER_ID`)*.

### 2. Obtener credenciales de Google Cloud (Gratis)
1. Ve a [Google Cloud Console](https://console.cloud.google.com/).
2. Crea un proyecto nuevo (ejemplo: `boda-qr`).
3. En el menú lateral, ve a **APIs y servicios** > **Biblioteca**.
4. Busca **Google Drive API** y haz clic en **Habilitar**.
5. Ve a **APIs y servicios** > **Credenciales**.
6. Haz clic en **Crear credenciales** > **Cuenta de servicio** (Service Account):
   - Asigna un nombre (ej: `subidor-boda`) y presiona **Crear y continuar**.
   - Rol: Puedes dejarlo vacío o asignar **Editor**. Presiona **Listo**.
7. En la lista de Cuentas de servicio, haz clic en el correo que se acaba de crear (ej: `subidor-boda@tu-proyecto.iam.gserviceaccount.com`).
8. Ve a la pestaña **Claves** (Keys) > **Agregar clave** > **Crear clave nueva** > Selecciona formato **JSON** y presiona **Crear**.
9. Se descargará un archivo `.json`. **Cámbiale el nombre a `service_account.json` y colócalo en la carpeta raíz de este proyecto**.

### 3. Dar permiso a la Cuenta de Servicio en tu carpeta de Drive
1. Vuelve a Google Drive a tu carpeta de la boda.
2. Haz clic derecho en la carpeta > **Compartir**.
3. Pega el correo de la cuenta de servicio (el que termina en `iam.gserviceaccount.com`).
4. Dale permisos de **Editor** y desmarca la casilla "Notificar a los usuarios". Haz clic en **Compartir**.

### 4. Configurar el archivo `.env`
Abre el archivo `.env` en esta carpeta y coloca los datos:
```env
COUPLE_NAMES=Ana & Carlos
EVENT_DATE=15 de Noviembre, 2026
DRIVE_FOLDER_ID=tu_codigo_de_carpeta_aqui
```

¡Listo! A partir de ese momento, cada foto o video subido desde el celular irá directo a tu carpeta de Google Drive.

---

## 🖨️ Imprimir la Tarjeta QR para las Mesas

1. Inicia el servidor y entra a: [http://localhost:5000/qr](http://localhost:5000/qr)
2. Escribe la URL de tu aplicativo publicado (o presiona el botón si ya está en internet).
3. Personaliza los nombres y la fecha si lo deseas.
4. Presiona **"Imprimir Tarjeta (Ctrl+P)"** o **"Descargar Tarjeta PNG"** para imprimirla en papel fotográfico o cartulina y colocarla en centros de mesa.

---

## 🌐 Publicación en Servidor Gratuito (Vercel)

El proyecto ya está preparado para **Vercel** (`vercel.json` y `api/index.py` incluidos):

1. Sube esta carpeta a un repositorio privado en **GitHub**.
2. Entra a [Vercel.com](https://vercel.com) (inicia sesión gratis con tu GitHub).
3. Haz clic en **Add New Project** e importa tu repositorio.
4. En la sección **Environment Variables**, añade:
   - `DRIVE_FOLDER_ID`: El ID de tu carpeta de Drive.
   - `COUPLE_NAMES`: Nombres de los novios.
   - `GOOGLE_SERVICE_ACCOUNT_JSON`: Pega todo el contenido de tu `service_account.json` en una sola línea.
5. Haz clic en **Deploy**.
6. Vercel te dará una URL HTTPS como: `https://boda-recuerdos.vercel.app`.
7. Esa URL es la que pones en el generador de QR para imprimir las tarjetas.
