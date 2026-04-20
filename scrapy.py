import instaloader  # Librería para interactuar con Instagram (scraping)
import os           # Manejo de archivos y carpetas del sistema
import json         # Guardar datos en formato JSON
import time         # Controlar pausas (evitar bloqueos)
import re           # Expresiones regulares (analizar texto)


# ─────────────────────────────
# LOGIN (AUTENTICACIÓN)
# ─────────────────────────────
def login(usuario, sessionid, csrftoken, ds_user_id):
    # Crear instancia principal de Instaloader
    loader = instaloader.Instaloader(quiet=True)

    # Cookies necesarias para simular sesión activa
    cookies = {
        "sessionid": sessionid,   # Identifica la sesión del usuario (clave principal)
        "csrftoken": csrftoken,   # Token de seguridad contra ataques CSRF
        "ds_user_id": ds_user_id  # ID interno del usuario (refuerza autenticación)
    }

    # Cargar sesión manualmente usando cookies (sin contraseña)
    loader.load_session(usuario, cookies)

    # Verificar si la sesión es válida
    if not loader.test_login():
        raise Exception("❌ Error de autenticación")

    print(f"\n✅ Sesión activa: @{usuario}")
    return loader  # Retornamos el objeto autenticado


# ─────────────────────────────
# OBTENER PERFIL
# ─────────────────────────────
def obtener_perfil(loader, objetivo):
    # Obtiene el perfil usando el contexto autenticado
    return instaloader.Profile.from_username(loader.context, objetivo)


# ─────────────────────────────
# PROCESAR POSTS
# ─────────────────────────────
def procesar_posts(perfil, loader, limite_posts, img_dir):
    data_posts = []  # Lista donde se guardarán los datos

    print("\n" + "="*50)
    print(f"📸 PROCESANDO {limite_posts} POSTS")
    print("="*50)

    # Recorremos los posts del perfil
    for i, post in enumerate(perfil.get_posts(), 1):

        # Limitar cantidad de posts
        if i > limite_posts:
            break

        # Determinar si es video o imagen
        tipo = "video" if post.is_video else "imagen"

        # Mostrar información básica
        print(f"\n[{i}] {'🎥 Video' if post.is_video else '📷 Imagen'}")
        print(f"❤️ {post.likes:,}  💬 {post.comments:,}")
        print(f"🔗 https://instagram.com/p/{post.shortcode}/")

        # ─── CAPTION ────────────────────────
        # Obtener texto, evitar None y limpiar saltos de línea
        caption = (post.caption or "").replace("\n", " ").strip()

        print(f"📝 {caption if caption else 'Sin descripción'}")

        # ─── ANALISIS DE TEXTO ──────────────
        # Buscar hashtags (#algo)
        hashtags = re.findall(r"#(\w+)", caption)

        # Buscar menciones (@usuario)
        menciones = re.findall(r"@(\w+)", caption)

        # Mostrar resultados del análisis
        print(f"🏷️ Hashtags ({len(hashtags)}): {hashtags}")
        print(f"👤 Menciones ({len(menciones)}): {menciones}")

        img_path = None  # Ruta de imagen local (si existe)

        # ─── DESCARGA DE IMÁGENES ───────────
        if not post.is_video:  # Solo descargar imágenes

            # Crear nombre único usando shortcode del post
            filename = os.path.join(img_dir, f"{post.shortcode}.jpg")

            # Evitar descargar si ya existe el archivo
            if not os.path.exists(filename):
                try:
                    loader.download_pic(filename, post.url, post.date_utc)
                    print("⬇️ Imagen descargada")
                except Exception as e:
                    print(f"⚠️ Error imagen: {e}")

            img_path = filename  # Guardar ruta

        # Guardar toda la información del post
        data_posts.append({
            "id": post.shortcode,
            "tipo": tipo,
            "likes": post.likes,
            "comentarios": post.comments,
            "caption": caption,
            "hashtags": hashtags,
            "menciones": menciones,
            "total_hashtags": len(hashtags),
            "total_menciones": len(menciones),
            "url": f"https://instagram.com/p/{post.shortcode}/",
            "imagen_local": img_path
        })

        # Pausa para evitar bloqueo por demasiadas peticiones
        time.sleep(1)

    return data_posts


# ─────────────────────────────
# OBTENER SEGUIDORES
# ─────────────────────────────
def obtener_seguidores(perfil, limite):
    seguidores = []

    print("\n" + "="*50)
    print(f"👥 PRIMEROS {limite} SEGUIDORES")
    print("="*50)

    try:
        # Recorrer seguidores
        for i, f in enumerate(perfil.get_followers(), 1):

            if i > limite:
                break

            print(f"[{i}] @{f.username}")
            seguidores.append(f.username)

    except Exception as e:
        print(f"⚠️ Error obteniendo seguidores: {e}")

    return seguidores


# ─────────────────────────────
# GUARDAR JSON
# ─────────────────────────────
def guardar_json(base_dir, objetivo, posts, seguidores):
    # Estructura final de datos
    data = {
        "usuario": objetivo,
        "posts": posts,
        "seguidores": seguidores
    }

    # Guardar en archivo JSON
    with open(f"{base_dir}/data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    print(f"\n💾 Guardado en {base_dir}/data.json")


# ─────────────────────────────
# MAIN (FLUJO PRINCIPAL)
# ─────────────────────────────
def main():
    print("="*50)
    print("🚀 INSTAGRAM SCRAPER + ANALYTICS (PRO)")
    print("="*50)

    print("\n📌 F12 → Application → Cookies → instagram.com")

    # ─── INPUT ─────────────────────────
    usuario = input("\n👤 Usuario: ").strip()
    sessionid = input("🔐 sessionid: ").strip()
    csrftoken = input("🔑 csrftoken: ").strip()
    ds_user_id = input("🆔 ds_user_id: ").strip()

    objetivo = input("\n🎯 Usuario a scrapear: ").strip().replace('@', '')
    limite_posts = int(input("📸 Número de posts: ") or 3)
    limite_seguidores = int(input("👥 Número de seguidores: ") or 10)

    try:
        # LOGIN
        loader = login(usuario, sessionid, csrftoken, ds_user_id)

        # PERFIL
        perfil = obtener_perfil(loader, objetivo)

        print("\n" + "="*50)
        print("📊 PERFIL")
        print("="*50)
        print(f"👤 @{perfil.username}")
        print(f"📛 {perfil.full_name or '—'}")
        print(f"👥 {perfil.followers:,} seguidores")
        print(f"📸 {perfil.mediacount:,} posts")
        print(f"🔒 Privado: {'Sí' if perfil.is_private else 'No'}")

        # ─── CREAR CARPETAS ─────────────
        base_dir = f"data_{objetivo}"
        img_dir = os.path.join(base_dir, "images")
        os.makedirs(img_dir, exist_ok=True)

        # POSTS
        posts = procesar_posts(perfil, loader, limite_posts, img_dir)

        # SEGUIDORES
        seguidores = obtener_seguidores(perfil, limite_seguidores)

        # GUARDAR RESULTADOS
        guardar_json(base_dir, objetivo, posts, seguidores)

        print("\n" + "="*50)
        print("✅ COMPLETADO")
        print("="*50)

    except Exception as e:
        print(f"\n❌ ERROR GENERAL: {e}")


# ─────────────────────────────
# EJECUCIÓN DEL PROGRAMA
# ─────────────────────────────
if __name__ == "__main__":
    # Solo se ejecuta si el archivo se corre directamente
    main()
