from pathlib import Path


ROOT = Path(__file__).parents[1]
TEMPLATES = ROOT / "templates"


def test_todas_las_paginas_funcionales_extienden_la_estructura_global():
    paginas = [
        path
        for path in TEMPLATES.rglob("*.html")
        if path.name != "base.html" and "components" not in path.parts
    ]

    assert paginas
    for pagina in paginas:
        contenido = pagina.read_text(encoding="utf-8")
        assert '{% extends "base.html" %}' in contenido, pagina


def test_formularios_post_conservan_csrf_y_acciones_de_salida():
    paginas_con_post = []
    for pagina in TEMPLATES.rglob("*.html"):
        contenido = pagina.read_text(encoding="utf-8")
        if 'method="post"' in contenido:
            paginas_con_post.append(pagina)
            assert "{% csrf_token %}" in contenido, pagina

    assert paginas_con_post
    assert "Cancelar" in (TEMPLATES / "espacios" / "form.html").read_text(
        encoding="utf-8"
    )
    assert "Volver" in (TEMPLATES / "reservas" / "detail.html").read_text(
        encoding="utf-8"
    )
    assert "Cancelar" in (TEMPLATES / "usuarios" / "form.html").read_text(
        encoding="utf-8"
    )


def test_listados_y_estados_reutilizan_componentes_visuales():
    archivos_con_estado = [
        TEMPLATES / "home.html",
        TEMPLATES / "espacios" / "list.html",
        TEMPLATES / "reservas" / "list.html",
        TEMPLATES / "reservas" / "historial_global.html",
        TEMPLATES / "usuarios" / "list.html",
    ]

    for archivo in archivos_con_estado:
        assert 'include "components/status_badge.html"' in archivo.read_text(
            encoding="utf-8"
        )

    for archivo in (
        TEMPLATES / "espacios" / "list.html",
        TEMPLATES / "reservas" / "list.html",
        TEMPLATES / "reservas" / "historial_global.html",
        TEMPLATES / "usuarios" / "list.html",
    ):
        assert "empty-state" in archivo.read_text(encoding="utf-8")
