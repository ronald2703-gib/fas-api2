import requests
from functools import wraps

from django.conf import settings
from django.contrib import messages
from django.shortcuts import render, redirect
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
                return redirect("product_list")
            if resp.status_code == 401:
                return render(request, "store/login.html", {"error": "Correo o contraseña incorrectos", "email": email})
            return render(request, "store/login.html", {"error": "La API respondió con un error inesperado", "email": email})
        except requests.exceptions.RequestException:
            return render(request, "store/login.html", {"error": "No se pudo conectar con la API", "email": email})
    return render(request, "store/login.html")


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
                return redirect("login")
            return render(request, "store/register.html", {
                "error": _api_error(resp, "No se pudo crear la cuenta"), "form": payload})
        except requests.exceptions.RequestException:
            return render(request, "store/register.html", {"error": "No se pudo conectar con la API", "form": payload})
    return render(request, "store/register.html")


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
    }
    errors = []
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
    return {"modo": modo, "product": product, "errors": errors or []}


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
