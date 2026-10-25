"""Pruebas del modelo de dominio del catálogo (validaciones y consultas)."""

import pytest

from src.catalogo import (
    Categoria,
    ErrorDominio,
    ProductoCombo,
    ProductoDestacado,
    ProductoPorPeso,
    ProductoSimple,
    UnidadMedida,
    exportar_catalogo,
)


def test_categoria_sin_nombre_lanza_error():
    # Act
    with pytest.raises(ErrorDominio) as error:
        Categoria("   ")

    # Assert
    assert "no puede estar vacío" in str(error.value)


def test_categoria_expone_nombre_y_descripcion():
    # Arrange
    bebidas = Categoria("Bebidas", "Frías y calientes")

    # Act
    datos = (bebidas.nombre, bebidas.descripcion, repr(bebidas))

    # Assert
    assert datos == ("Bebidas", "Frías y calientes", "Categoria('Bebidas')")


@pytest.mark.parametrize(
    "nombre, precio, stock, mensaje",
    [
        ("", 100.0, 1, "nombre del producto"),
        ("Agua", -1.0, 1, "precio base"),
        ("Agua", 100.0, -1, "stock"),
    ],
)
def test_producto_con_datos_invalidos_lanza_error(nombre, precio, stock, mensaje):
    # Arrange
    bebidas = Categoria("Bebidas")

    # Act
    with pytest.raises(ErrorDominio) as error:
        ProductoSimple(nombre, precio, stock, bebidas)

    # Assert
    assert mensaje in str(error.value)


def test_producto_rechaza_categoria_y_unidad_de_otro_tipo():
    # Arrange
    bebidas = Categoria("Bebidas")

    # Act
    with pytest.raises(ErrorDominio) as error_categoria:
        ProductoSimple("Agua", 100.0, 1, "Bebidas")
    with pytest.raises(ErrorDominio) as error_unidad:
        ProductoSimple("Agua", 100.0, 1, bebidas, unidad_venta="kg")

    # Assert
    assert "Categoria" in str(error_categoria.value)
    assert "UnidadMedida" in str(error_unidad.value)


def test_precio_publicado_con_y_sin_unidad_de_venta():
    # Arrange
    fiambreria = Categoria("Fiambrería")
    kilo = UnidadMedida("kilogramo", "kg", "masa")
    queso = ProductoPorPeso("Queso", 8000.0, 5.0, fiambreria, kilo)
    pan = ProductoSimple("Pan", 1200.0, 10, fiambreria)

    # Act
    publicados = (queso.precio_publicado, pan.precio_publicado)

    # Assert
    assert publicados == ("$ 8000.00 / kg", "$ 1200.00")
    assert queso.unidad_venta is kilo


def test_producto_deshabilitado_deja_de_estar_disponible_y_vuelve():
    # Arrange
    bebidas = Categoria("Bebidas")
    agua = ProductoSimple("Agua", 900.0, 10, bebidas)

    # Act
    agua.deshabilitar()
    disponible_deshabilitado = agua.disponible
    agua.habilitar()

    # Assert
    assert disponible_deshabilitado is False
    assert agua.disponible is True


def test_clasificar_en_una_nueva_principal_desmarca_la_anterior():
    # Arrange
    bebidas = Categoria("Bebidas")
    gaseosas = Categoria("Gaseosas")
    cola = ProductoSimple("Cola", 1500.0, 10, bebidas)

    # Act
    cola.clasificar_en(gaseosas, es_principal=True)

    # Assert
    assert cola.categoria_principal() is gaseosas
    assert [pc.es_principal for pc in cola.categorias()] == [False, True]
    assert "secundaria" in repr(cola.categorias()[0])


def test_clasificar_dos_veces_en_la_misma_categoria_lanza_error():
    # Arrange
    bebidas = Categoria("Bebidas")
    cola = ProductoSimple("Cola", 1500.0, 10, bebidas)

    # Act
    with pytest.raises(ErrorDominio) as error_repetida:
        cola.clasificar_en(bebidas)
    with pytest.raises(ErrorDominio) as error_tipo:
        cola.clasificar_en("Bebidas")

    # Assert
    assert "ya está clasificado" in str(error_repetida.value)
    assert "instancia de Categoria" in str(error_tipo.value)


@pytest.mark.parametrize(
    "cantidad, mensaje", [("1", "numérica"), (0, "mayor que cero")]
)
def test_producto_por_peso_rechaza_cantidades_invalidas(cantidad, mensaje):
    # Arrange
    fiambreria = Categoria("Fiambrería")
    queso = ProductoPorPeso("Queso", 8000.0, 5.0, fiambreria)

    # Act
    with pytest.raises(ErrorDominio) as error:
        queso.precio_final(cantidad)

    # Assert
    assert mensaje in str(error.value)


def test_combo_con_datos_invalidos_lanza_error():
    # Arrange
    combos = Categoria("Combos")
    hamburguesa = ProductoSimple("Hamburguesa", 4500.0, 20, combos)
    papas = ProductoSimple("Papas", 2000.0, 30, combos)

    # Act
    with pytest.raises(ErrorDominio) as error_uno:
        ProductoCombo("Solo", [hamburguesa], 0.1, combos)
    with pytest.raises(ErrorDominio) as error_tipo:
        ProductoCombo("Raro", [hamburguesa, "papas"], 0.1, combos)
    with pytest.raises(ErrorDominio) as error_descuento:
        ProductoCombo("Regalado", [hamburguesa, papas], 1.0, combos)

    # Assert
    assert "al menos 2" in str(error_uno.value)
    assert "deben ser Producto" in str(error_tipo.value)
    assert "rango" in str(error_descuento.value)


def test_combo_disponible_depende_de_sus_componentes():
    # Arrange
    combos = Categoria("Combos")
    hamburguesa = ProductoSimple("Hamburguesa", 4500.0, 20, combos)
    papas = ProductoSimple("Papas", 2000.0, 30, combos)
    combo = ProductoCombo("Combo", [hamburguesa, papas], 0.1, combos)

    # Act
    papas.deshabilitar()

    # Assert
    assert combo.disponible is False
    assert combo.componentes() == (hamburguesa, papas)


def test_producto_destacado_valida_y_expone_su_orden():
    # Arrange
    bebidas = Categoria("Bebidas")
    agua = ProductoSimple("Agua", 900.0, 10, bebidas)

    # Act
    destacado = ProductoDestacado(agua, 1)
    with pytest.raises(ErrorDominio):
        ProductoDestacado("Agua", 1)
    with pytest.raises(ErrorDominio):
        ProductoDestacado(agua, -1)

    # Assert
    assert destacado.producto is agua
    assert destacado.orden_vidriera == 1
    assert repr(destacado) == "ProductoDestacado('Agua', orden=1)"


class FichaDeOtroSistema:
    """Clase ajena al catálogo: cumple el contrato Exportable sin heredar."""

    def exportar(self) -> str:
        return "POS|POS-01|Agua mineral"


def test_exportar_catalogo_mezcla_productos_y_fichas_externas():
    # Arrange
    bebidas = Categoria("Bebidas")
    agua = ProductoSimple("Agua", 900.0, 10, bebidas)
    ficha = FichaDeOtroSistema()

    # Act
    exportado = exportar_catalogo([agua, ficha])

    # Assert
    assert exportado == ["PRD|Agua|$ 900.00", "POS|POS-01|Agua mineral"]
    assert repr(agua) == "ProductoSimple('Agua')"
