import requests
from datetime import datetime, timezone as dt_timezone
from functools import wraps

from django.conf import settings
from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme
from urllib.parse import quote
from django.views.decorators.http import require_POST

TIMEOUT = 30  # Render (plan gratis) puede tardar en "despertar"
LOW_STOCK = 5


# ---------------------------------------------------------------- helpers API
def _url(path):
    return f"{settings.API_URL}{path}"


def _auth_headers(request):
    return {"Authorization": f"Bearer {request.session.get('access_token', '')}"}


def _session_expired(request):
    """Token vencido o invalido: limpiamos la sesion y mandamos a login."""
    request.session.flush()
    messages.warning(request, "Tu sesión expiró. Inicia sesión de nuevo.")
    return redirect("login")


def _fetch_products():
    try:
        resp = requests.get(_url("/products"), timeout=TIMEOUT)
        if resp.status_code == 200:
            return resp.json()
    except requests.exceptions.RequestException:
        pass
    return None  # None = la API no respondio


def _api_error(resp, default):
    try:
        detail = resp.json().get("detail", default)
    except ValueError:
        return default
    return detail if isinstance(detail, str) else "Datos inválidos, revisa el formulario."


def admin_required(view):
    """Solo deja pasar a usuarios con sesion y rol admin."""
    @wraps(view)
    def wrapper(request, *args, **kwargs):
        if not request.session.get("access_token"):
            messages.warning(request, "Debes iniciar sesión para continuar.")
            return redirect("login")
        if request.session.get("rol") != "admin":
            messages.error(request, "No tienes permisos de administrador.")
            return redirect("product_list")
        return view(request, *args, **kwargs)
    return wrapper


def _safe_next(request):
    """Devuelve la URL 'next' solo si apunta a este mismo sitio (evita open redirect)."""
    nxt = request.POST.get("next") or request.GET.get("next") or ""
    if nxt and url_has_allowed_host_and_scheme(nxt, allowed_hosts={request.get_host()},
                                               require_https=request.is_secure()):
        return nxt
    return ""


def client_required(view):
    """Deja pasar solo a clientes con sesion. Sin sesion -> login (y vuelve aqui); admin -> su dashboard."""
    @wraps(view)
    def wrapper(request, *args, **kwargs):
        if not request.session.get("access_token"):
            messages.warning(request, "Inicia sesión para continuar.")
            return redirect(f"{reverse('login')}?next={quote(request.get_full_path())}")
        if request.session.get("rol") == "admin":
            messages.info(request, "Las compras son para cuentas de cliente.")
            return redirect("dashboard")
        return view(request, *args, **kwargs)
    return wrapper


def _parse_dt(value):
    """La API devuelve la fecha en ISO (UTC, sin zona). La volvemos 'aware' para mostrarla en hora local."""
    if not isinstance(value, str):
        return None
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    return timezone.make_aware(dt, dt_timezone.utc) if timezone.is_naive(dt) else dt


# ------------------------------------------------------------------- catalogo
def product_list(request):
    products = _fetch_products()
    api_down = products is None
    products = products or []

    q = request.GET.get("q", "").strip().lower()
    categoria = request.GET.get("categoria", "").strip()
    categorias = sorted({p.get("categoria", "") for p in products if p.get("categoria")})

    if q:
        products = [p for p in products
                    if q in p.get("nombre", "").lower() or q in p.get("descripcion", "").lower()]
    if categoria:
        products = [p for p in products if p.get("categoria") == categoria]

    return render(request, "store/product_list.html", {
        "products": products,
        "categorias": categorias,
        "q": request.GET.get("q", ""),
        "categoria_sel": categoria,
        "api_down": api_down,
        "low_stock": LOW_STOCK,
    })


# ---------------------------------------------------------------------- auth
def login_view(request):
    if request.method == "POST":
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "")
        try:
            resp = requests.post(_url("/auth/login"), json={"email": email, "password": password}, timeout=TIMEOUT)
            if resp.status_code == 200:
                token = resp.json().get("access_token")
                # Consultamos el perfil para conocer nombre y rol
                me = requests.get(_url("/users/me"), headers={"Authorization": f"Bearer {token}"}, timeout=TIMEOUT)
                perfil = me.json() if me.status_code == 200 else {}
                request.session["access_token"] = token
                request.session["user_email"] = email
                request.session["user_nombre"] = perfil.get("nombre", email)
                request.session["rol"] = perfil.get("rol", "cliente")
                messages.success(request, f"¡Bienvenido, {request.session['user_nombre']}!")
                if request.session["rol"] == "admin":
                    return redirect("dashboard")
                return redirect(_safe_next(request) or "product_list")
            ctx = {"email": email, "next": _safe_next(request)}
            if resp.status_code == 401:
                return render(request, "store/login.html", {**ctx, "error": "Correo o contraseña incorrectos"})
            return render(request, "store/login.html", {**ctx, "error": "La API respondió con un error inesperado"})
        except requests.exceptions.RequestException:
            return render(request, "store/login.html", {"email": email, "next": _safe_next(request),
                                                        "error": "No se pudo conectar con la API"})
    return render(request, "store/login.html", {"next": _safe_next(request)})


def register_view(request):
    if request.method == "POST":
        payload = {
            "nombre": request.POST.get("nombre", "").strip(),
            "email": request.POST.get("email", "").strip(),
            "password": request.POST.get("password", ""),
        }
        try:
            resp = requests.post(_url("/users"), json=payload, timeout=TIMEOUT)
            if resp.status_code == 201:
                messages.success(request, "Cuenta creada. Ya puedes iniciar sesión.")
                nxt = _safe_next(request)
                return redirect(f"{reverse('login')}?next={quote(nxt)}" if nxt else "login")
            return render(request, "store/register.html", {
                "error": _api_error(resp, "No se pudo crear la cuenta"), "form": payload, "next": _safe_next(request)})
        except requests.exceptions.RequestException:
            return render(request, "store/register.html", {
                "error": "No se pudo conectar con la API", "form": payload, "next": _safe_next(request)})
    return render(request, "store/register.html", {"next": _safe_next(request)})


def logout_view(request):
    request.session.flush()  # elimina el token JWT y el rol de la sesion
    messages.info(request, "Sesión cerrada correctamente.")
    return redirect("product_list")


# ------------------------------------------------------ dashboard (CRUD admin)
@admin_required
def dashboard(request):
    products = _fetch_products()
    api_down = products is None
    products = products or []

    stats = {
        "total": len(products),
        "unidades": sum(p.get("stock", 0) for p in products),
        "valor": sum(p.get("precio", 0) * p.get("stock", 0) for p in products),
        "bajo_stock": sum(1 for p in products if p.get("stock", 0) <= LOW_STOCK),
    }
    return render(request, "store/dashboard.html", {
        "products": products, "stats": stats, "api_down": api_down, "low_stock": LOW_STOCK})


def _parse_product(post):
    """Valida el formulario y devuelve (datos, errores)."""
    data = {
        "nombre": post.get("nombre", "").strip(),
        "descripcion": post.get("descripcion", "").strip(),
        "categoria": post.get("categoria", "").strip(),
        "precio": post.get("precio", "").strip(),
        "stock": post.get("stock", "").strip(),
        # URL escrita a mano o imagen subida (la web la reduce y la manda como data-URI)
        "imagen": (post.get("imagen_url", "").strip() or post.get("imagen", "").strip()),
    }
    errors = []
    if data["imagen"] and not data["imagen"].lower().startswith(("http://", "https://", "data:image/")):
        errors.append("La imagen debe ser una URL http(s) o un archivo de imagen.")
    elif len(data["imagen"]) > 350_000:
        errors.append("La imagen es demasiado pesada. Usa una más pequeña.")
    if not data["nombre"]:
        errors.append("El nombre es obligatorio.")
    if not data["categoria"]:
        errors.append("La categoría es obligatoria.")
    try:
        data["precio"] = float(data["precio"])
        if data["precio"] <= 0:
            errors.append("El precio debe ser mayor que 0.")
    except ValueError:
        errors.append("El precio debe ser un número.")
    try:
        data["stock"] = int(data["stock"])
        if data["stock"] < 0:
            errors.append("El stock no puede ser negativo.")
    except ValueError:
        errors.append("El stock debe ser un número entero.")
    return data, errors


def _form_ctx(modo, product, errors=None):
    img = product.get("imagen_url") or product.get("imagen") or ""
    return {"modo": modo, "product": product, "errors": errors or [],
            "img_data": img if img.startswith("data:") else "",
            "img_url": "" if img.startswith("data:") else img}


@admin_required
def product_create(request):
    if request.method == "POST":
        data, errors = _parse_product(request.POST)
        if errors:
            return render(request, "store/product_form.html", _form_ctx("crear", request.POST, errors))
        try:
            resp = requests.post(_url("/products"), json=data, headers=_auth_headers(request), timeout=TIMEOUT)
        except requests.exceptions.RequestException:
            return render(request, "store/product_form.html",
                          _form_ctx("crear", request.POST, ["No se pudo conectar con la API."]))
        if resp.status_code == 401:
            return _session_expired(request)
        if resp.status_code == 201:
            messages.success(request, f"Producto «{data['nombre']}» creado correctamente.")
            return redirect("dashboard")
        return render(request, "store/product_form.html",
                      _form_ctx("crear", request.POST, [_api_error(resp, "No se pudo crear el producto.")]))
    return render(request, "store/product_form.html", _form_ctx("crear", {}))


@admin_required
def product_update(request, product_id):
    if request.method == "POST":
        data, errors = _parse_product(request.POST)
        product = dict(request.POST.items(), id=product_id)
        if errors:
            return render(request, "store/product_form.html", _form_ctx("editar", product, errors))
        try:
            resp = requests.put(_url(f"/products/{product_id}"), json=data,
                                headers=_auth_headers(request), timeout=TIMEOUT)
        except requests.exceptions.RequestException:
            return render(request, "store/product_form.html",
                          _form_ctx("editar", product, ["No se pudo conectar con la API."]))
        if resp.status_code == 401:
            return _session_expired(request)
        if resp.status_code == 200:
            messages.success(request, f"Producto «{data['nombre']}» actualizado.")
            return redirect("dashboard")
        return render(request, "store/product_form.html",
                      _form_ctx("editar", product, [_api_error(resp, "No se pudo actualizar el producto.")]))

    # GET: precargamos el formulario con los datos actuales
    try:
        resp = requests.get(_url(f"/products/{product_id}"), timeout=TIMEOUT)
    except requests.exceptions.RequestException:
        messages.error(request, "No se pudo conectar con la API.")
        return redirect("dashboard")
    if resp.status_code != 200:
        messages.error(request, "El producto no existe o ya fue eliminado.")
        return redirect("dashboard")
    return render(request, "store/product_form.html", _form_ctx("editar", resp.json()))


@admin_required
@require_POST
def product_delete(request, product_id):
    try:
        resp = requests.delete(_url(f"/products/{product_id}"), headers=_auth_headers(request), timeout=TIMEOUT)
    except requests.exceptions.RequestException:
        messages.error(request, "No se pudo conectar con la API.")
        return redirect("dashboard")
    if resp.status_code == 401:
        return _session_expired(request)
    if resp.status_code == 200:
        messages.success(request, "Producto eliminado correctamente.")
    else:
        messages.error(request, _api_error(resp, "No se pudo eliminar el producto."))
    return redirect("dashboard")


# ------------------------------------------------------------ compras (cliente)
@require_POST
def comprar(request, product_id):
    """Guarda el producto como pedido PENDIENTE en 'Mis pedidos'. Sin sesion -> login."""
    back = _safe_next(request) or reverse("product_list")
    if not request.session.get("access_token"):
        messages.warning(request, "Inicia sesión para comprar.")
        return redirect(f"{reverse('login')}?next={quote(back)}")
    if request.session.get("rol") == "admin":
        messages.info(request, "Las compras son para cuentas de cliente.")
        return redirect(back)
    try:
        resp = requests.post(_url("/orders"), json={"items": [{"product_id": product_id, "cantidad": 1}]},
                             headers=_auth_headers(request), timeout=TIMEOUT)
    except requests.exceptions.RequestException:
        messages.error(request, "No se pudo conectar con la API. Inténtalo de nuevo.")
        return redirect(back)
    if resp.status_code == 401:
        return _session_expired(request)
    if resp.status_code == 201:
        messages.success(request, "Producto guardado en tus pedidos. Confírmalo cuando estés listo para comprar.")
    else:
        messages.error(request, _api_error(resp, "No se pudo guardar el pedido."))
    return redirect(back)


ESTADOS = ("pendiente", "comprado", "cancelado")


@client_required
def mis_pedidos(request):
    try:
        resp = requests.get(_url("/orders/me"), headers=_auth_headers(request), timeout=TIMEOUT)
    except requests.exceptions.RequestException:
        resp = None
    api_down = resp is None or resp.status_code not in (200, 401)
    if resp is not None and resp.status_code == 401:
        return _session_expired(request)
    orders = resp.json() if resp is not None and resp.status_code == 200 else []

    for o in orders:
        o["fecha_dt"] = _parse_dt(o.get("fecha"))
        o["corto"] = o["id"][-6:].upper()
        for it in o.get("items", []):
            it["subtotal"] = it.get("cantidad", 0) * it.get("precio_unitario", 0)

    stats = {
        "pendientes": sum(1 for o in orders if o["estado"] == "pendiente"),
        "por_pagar": sum(o["total"] for o in orders if o["estado"] == "pendiente"),
        "comprados": sum(1 for o in orders if o["estado"] == "comprado"),
    }
    filtro = request.GET.get("estado", "")
    if filtro in ESTADOS:
        orders = [o for o in orders if o["estado"] == filtro]
    return render(request, "store/mis_pedidos.html", {
        "orders": orders, "stats": stats, "filtro": filtro, "api_down": api_down})


@client_required
@require_POST
def pedido_estado(request, order_id):
    estado = request.POST.get("estado", "")
    if estado not in ("comprado", "cancelado"):
        messages.error(request, "Acción no válida.")
        return redirect("mis_pedidos")
    try:
        resp = requests.patch(_url(f"/orders/{order_id}/estado"), json={"estado": estado},
                              headers=_auth_headers(request), timeout=TIMEOUT)
    except requests.exceptions.RequestException:
        messages.error(request, "No se pudo conectar con la API.")
        return redirect("mis_pedidos")
    if resp.status_code == 401:
        return _session_expired(request)
    if resp.status_code == 200:
        messages.success(request, "¡Compra confirmada!" if estado == "comprado" else "Pedido cancelado.")
    else:
        messages.error(request, _api_error(resp, "No se pudo actualizar el pedido."))
    return redirect("mis_pedidos")


def robots_txt(request):
    """robots.txt: indexar el catálogo y dejar fuera las zonas privadas."""
    lines = [
        "User-agent: *",
        "Allow: /",
        "Disallow: /dashboard/",
        "Disallow: /mis-pedidos/",
        "Disallow: /comprar/",
        "Disallow: /login/",
        "Disallow: /register/",
    ]
    return HttpResponse("\n".join(lines) + "\n", content_type="text/plain")
