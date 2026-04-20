import instaloader   # Librería para interactuar con Instagram
import os            # Manejo de carpetas y archivos
import json          # Guardar datos en formato JSON
import time          # Para controlar tiempos (evitar bloqueos)
import re            # Expresiones regulares (hashtags y menciones)

print("="*50)
print("🚀 INSTAGRAM SCRAPER + ANALYTICS")
print("="*50)

# Instrucción para obtener cookies desde el navegador
print("\n📌 F12 → Application → Cookies → instagram.com")

# ─── INPUT DEL USUARIO ─────────────────────────────
# Credenciales (cookies)
usuario = input("\n👤 Usuario: ").strip()
sessionid = input("🔐 sessionid: ").strip()
csrftoken = input("🔑 csrftoken: ").strip()
ds_user_id = input("🆔 ds_user_id (opcional): ").strip()

# Parámetros del scraping
objetivo = input("\n🎯 Usuario a scrapear: ").strip().replace('@', '')
limite_posts = int(input("📸 Número de posts: ") or 3)
limite_seguidores = int(input("👥 Número de seguidores: ") or 10)

# ─── LOGIN ─────────────────────────────
# Inicializa el objeto principal de Instaloader
loader = instaloader.Instaloader(quiet=True)

# Se crean las cookies necesarias para autenticación
cookies = {"sessionid": sessionid, "csrftoken": csrftoken}

# Si existe ds_user_id se agrega (mejora estabilidad)
if ds_user_id:
    cookies["ds_user_id"] = ds_user_id

# Se carga la sesión manualmente usando cookies
loader.load_session(usuario, cookies)

# Se verifica si la sesión es válida
if not loader.test_login():
    print("\n❌ Error de autenticación")
    exit()

print(f"\n✅ Sesión activa: @{usuario}")

# ─── OBTENER PERFIL ─────────────────────
# Se obtiene el perfil del usuario objetivo
perfil = instaloader.Profile.from_username(loader.context, objetivo)

# Mostrar información básica del perfil
print("\n" + "="*50)
print("📊 PERFIL")
print("="*50)
print(f"👤 @{perfil.username}")
print(f"📛 {perfil.full_name or '—'}")
print(f"👥 {perfil.followers:,} seguidores")
print(f"📸 {perfil.mediacount:,} posts")
print(f"🔒 Privado: {'Sí' if perfil.is_private else 'No'}")

# ─── CREAR CARPETAS ─────────────────────
# Carpeta base donde se guardarán datos
base_dir = f"data_{objetivo}"

# Carpeta específica para imágenes
img_dir = os.path.join(base_dir, "images")

# Crea la carpeta si no existe
os.makedirs(img_dir, exist_ok=True)

# Lista donde se almacenarán los posts
data_posts = []

# ─── PROCESAR POSTS ─────────────────────
print("\n" + "="*50)
print(f"📸 PROCESANDO {limite_posts} POSTS")
print("="*50)

# Iterar sobre los posts del perfil
for i, post in enumerate(perfil.get_posts(), 1):

    # Limitar número de posts
    if i > limite_posts:
        break

    # Determinar tipo de contenido
    tipo = "video" if post.is_video else "imagen"

    # Mostrar info básica en consola
    print(f"\n[{i}] {'🎥 Video' if post.is_video else '📷 Imagen'}")
    print(f"❤️ {post.likes:,}  💬 {post.comments:,}")
    print(f"🔗 https://instagram.com/p/{post.shortcode}/")

    # ─── CAPTION ────────────────────────
    # Obtener texto del post, limpiar saltos de línea
    caption = (post.caption or "").replace("\n", " ").strip()

    # Mostrar caption completo
    if caption:
        print(f"📝 {caption}")
    else:
        print("📝 Sin descripción")

    # ─── ANALISIS DE TEXTO ──────────────
    # Extraer hashtags (#algo)
    hashtags = re.findall(r"#(\w+)", caption)

    # Extraer menciones (@usuario)
    menciones = re.findall(r"@(\w+)", caption)

    # Contar elementos
    total_hashtags = len(hashtags)
    total_menciones = len(menciones)

    # Mostrar resultados
    print(f"🏷️ Hashtags ({total_hashtags}): {hashtags}")
    print(f"👤 Menciones ({total_menciones}): {menciones}")

    # Variable para guardar ruta de imagen
    img_path = None

    # ─── DESCARGA DE IMÁGENES ───────────
    # Solo descarga si NO es video
    if not post.is_video:

        # Nombre del archivo basado en shortcode (único)
        filename = os.path.join(img_dir, f"{post.shortcode}.jpg")

        # Evitar descargar si ya existe
        if not os.path.exists(filename):
            try:
                # Descargar imagen
                loader.download_pic(filename, post.url, post.date_utc)
                print("⬇️ Imagen descargada")
            except:
                print("⚠️ Error imagen")

        # Guardar ruta de imagen
        img_path = filename

    # ─── GUARDAR DATOS DEL POST ─────────
    data_posts.append({
        "id": post.shortcode,
        "tipo": tipo,
        "likes": post.likes,
        "comentarios": post.comments,
        "caption": caption,
        "hashtags": hashtags,
        "menciones": menciones,
        "total_hashtags": total_hashtags,
        "total_menciones": total_menciones,
        "url": f"https://instagram.com/p/{post.shortcode}/",
        "imagen_local": img_path
    })

    # Pausa para evitar bloqueo por demasiadas requests
    time.sleep(1)

# ─── SEGUIDORES ─────────────────────────
seguidores = []

print("\n" + "="*50)
print(f"👥 PRIMEROS {limite_seguidores} SEGUIDORES")
print("="*50)

try:
    # Iterar seguidores
    for i, f in enumerate(perfil.get_followers(), 1):

        # Limitar cantidad
        if i > limite_seguidores:
            break

        # Mostrar en consola
        print(f"[{i}] @{f.username}")

        # Guardar en lista
        seguidores.append(f.username)

except:
    print("⚠️ No se pudieron obtener seguidores")

# ─── GUARDAR JSON ──────────────────────
data = {
    "usuario": objetivo,
    "posts": data_posts,
    "seguidores": seguidores
}

# Guardar archivo JSON
with open(f"{base_dir}/data.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=4, ensure_ascii=False)

print(f"\n💾 Guardado en {base_dir}/data.json")

print("\n" + "="*50)
print("✅ COMPLETADO")
print("="*50)