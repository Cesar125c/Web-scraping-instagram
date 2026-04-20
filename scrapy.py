import instaloader   # Librería para interactuar con Instagram
import os            # Manejo de carpetas y archivos
import json          # Guardar datos en formato JSON
import time          # Para controlar tiempos (evitar bloqueos)
import re            # Expresiones regulares (hashtags y menciones)

print("="*50)  # Línea decorativa
print("🚀 INSTAGRAM SCRAPER + ANALYTICS")  # Título del programa
print("="*50)

# Instrucción para obtener cookies desde el navegador
print("\n📌 F12 → Application → Cookies → instagram.com")

# ─── INPUT DEL USUARIO ─────────────────────────────

usuario = input("\n👤 Usuario: ").strip()  # Usuario con sesión activa
sessionid = input("🔐 sessionid: ").strip()  # Cookie principal de sesión
csrftoken = input("🔑 csrftoken: ").strip()  # Token de seguridad
ds_user_id = input("🆔 ds_user_id: ").strip()  # ID interno del usuario (AHORA OBLIGATORIO)

# Validación: ds_user_id no puede estar vacío
if not ds_user_id:
    print("❌ ds_user_id es obligatorio para continuar")
    exit()

# Usuario objetivo a scrapear
objetivo = input("\n🎯 Usuario a scrapear: ").strip().replace('@', '')

# Límites (con valores por defecto si el usuario no escribe nada)
limite_posts = int(input("📸 Número de posts: ") or 3)
limite_seguidores = int(input("👥 Número de seguidores: ") or 10)

# ─── LOGIN ─────────────────────────────

loader = instaloader.Instaloader(quiet=True)  
# Inicializa Instaloader (quiet=True evita mensajes innecesarios)

# Cookies completas (ahora ds_user_id es obligatorio)
cookies = {
    "sessionid": sessionid,
    "csrftoken": csrftoken,
    "ds_user_id": ds_user_id
}

# Carga la sesión usando cookies (simula sesión del navegador)
loader.load_session(usuario, cookies)

# Verifica si la sesión es válida
if not loader.test_login():
    print("\n❌ Error de autenticación")
    exit()

print(f"\n✅ Sesión activa: @{usuario}")  # Confirmación de login exitoso

# ─── OBTENER PERFIL ─────────────────────

perfil = instaloader.Profile.from_username(loader.context, objetivo)  
# Obtiene el perfil del usuario objetivo

print("\n" + "="*50)
print("📊 PERFIL")
print("="*50)

print(f"👤 @{perfil.username}")  # Username
print(f"📛 {perfil.full_name or '—'}")  # Nombre completo (si no hay, muestra —)
print(f"👥 {perfil.followers:,} seguidores")  # Cantidad de seguidores
print(f"📸 {perfil.mediacount:,} posts")  # Total de posts
print(f"🔒 Privado: {'Sí' if perfil.is_private else 'No'}")  # Estado de privacidad

# ─── CREAR CARPETAS ─────────────────────

base_dir = f"data_{objetivo}"  # Carpeta base
img_dir = os.path.join(base_dir, "images")  # Carpeta para imágenes

os.makedirs(img_dir, exist_ok=True)  
# Crea las carpetas si no existen

data_posts = []  # Lista donde se guardarán los posts

# ─── PROCESAR POSTS ─────────────────────

print("\n" + "="*50)
print(f"📸 PROCESANDO {limite_posts} POSTS")
print("="*50)

for i, post in enumerate(perfil.get_posts(), 1):  
    # Recorre los posts del perfil con contador

    if i > limite_posts:
        break  # Detiene el bucle al llegar al límite

    tipo = "video" if post.is_video else "imagen"  
    # Determina tipo de contenido

    print(f"\n[{i}] {'🎥 Video' if post.is_video else '📷 Imagen'}")
    print(f"❤️ {post.likes:,}  💬 {post.comments:,}")

    print(f"🔗 https://instagram.com/p/{post.shortcode}/")  
    # URL del post

    # ─── CAPTION ────────────────────────

    caption = (post.caption or "").replace("\n", " ").strip()  
    # Limpia el texto del post

    if caption:
        print(f"📝 {caption}")
    else:
        print("📝 Sin descripción")

    # ─── ANALISIS DE TEXTO ──────────────

    hashtags = re.findall(r"#(\w+)", caption)  
    # Extrae hashtags

    menciones = re.findall(r"@(\w+)", caption)  
    # Extrae menciones

    total_hashtags = len(hashtags)
    total_menciones = len(menciones)

    print(f"🏷️ Hashtags ({total_hashtags}): {hashtags}")
    print(f"👤 Menciones ({total_menciones}): {menciones}")

    img_path = None  # Ruta de la imagen

    # ─── DESCARGA DE IMÁGENES ───────────

    if not post.is_video:  # Solo si es imagen

        filename = os.path.join(img_dir, f"{post.shortcode}.jpg")  
        # Nombre del archivo

        if not os.path.exists(filename):  
            # Evita descargar duplicados
            try:
                loader.download_pic(filename, post.url, post.date_utc)
                print("⬇️ Imagen descargada")
            except:
                print("⚠️ Error imagen")

        img_path = filename  # Guarda ruta local

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

    time.sleep(1)  # Pausa para evitar bloqueo

# ─── SEGUIDORES ─────────────────────────

seguidores = []

print("\n" + "="*50)
print(f"👥 PRIMEROS {limite_seguidores} SEGUIDORES")
print("="*50)

try:
    for i, f in enumerate(perfil.get_followers(), 1):

        if i > limite_seguidores:
            break

        print(f"[{i}] @{f.username}")
        seguidores.append(f.username)

except:
    print("⚠️ No se pudieron obtener seguidores")

# ─── GUARDAR JSON ──────────────────────

data = {
    "usuario": objetivo,
    "posts": data_posts,
    "seguidores": seguidores
}

with open(f"{base_dir}/data.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=4, ensure_ascii=False)
# Guarda los datos en JSON

print(f"\n💾 Guardado en {base_dir}/data.json")

print("\n" + "="*50)
print("✅ COMPLETADO")
print("="*50)
