"""
catalogo.py: modelo de dominio de Food Store.

Contiene el catálogo completo: productos (simples, por peso y combos),
categorías, unidades de medida, el vínculo de clasificación, la
decisión de diseño sobre productos destacados y el contrato de
exportación (Protocol) que permite exportar productos propios junto
con fichas de un sistema de caja de terceros.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Protocol

# Excepciones de dominio


class ErrorDominio(ValueError):
    """Excepción para violaciones de las reglas de negocio del catálogo.

    Hereda de ValueError a propósito: quien quiera atrapar únicamente
    ValueError (sin conocer esta clase) sigue funcionando igual.
    """


# Objeto de datos inmutable


@dataclass(frozen=True)
class UnidadMedida:
    """Unidad en la que se vende un producto (kg, g, L, u).

    No muta en runtime.
    """

    nombre: str
    simbolo: str
    tipo: str  # "masa", "volumen" o "unidad" (dato descriptivo)


# Categoría


class Categoria:
    """Agrupa productos del catálogo (p. ej. Bebidas, Gaseosas, Fiambrería)."""

    def __init__(self, nombre: str, descripcion: str = "") -> None:
        if not nombre or not nombre.strip():
            raise ErrorDominio("El nombre de la categoría no puede estar vacío.")
        self._nombre = nombre
        self._descripcion = descripcion

    @property
    def nombre(self) -> str:
        return self._nombre

    @property
    def descripcion(self) -> str:
        return self._descripcion

    def __repr__(self) -> str:
        return f"Categoria({self._nombre!r})"


# Vínculo Producto-Categoria (composición: lo fabrica el propio Producto)


class ProductoCategoria:
    """Vínculo entre un producto y una categoría.

    El código cliente NUNCA instancia esta clase directamente: nace
    exclusivamente dentro de Producto (constructor y clasificar_en).
    Por eso no se expone ningún setter público: la única forma de
    cambiar cuál es la clasificación principal es que el propio
    Producto (su dueño) invoque el método protegido _marcar_principal.
    """

    def __init__(self, categoria: Categoria, es_principal: bool) -> None:
        self._categoria = categoria
        self._es_principal = es_principal

    @property
    def categoria(self) -> Categoria:
        return self._categoria

    @property
    def es_principal(self) -> bool:
        return self._es_principal

    def _marcar_principal(self, valor: bool) -> None:
        """Protegido (# en el diagrama): solo lo invoca el Producto dueño."""
        self._es_principal = valor

    def __repr__(self) -> str:
        marca = "principal" if self._es_principal else "secundaria"
        return f"ProductoCategoria({self._categoria.nombre!r}, {marca})"


# Producto (clase abstracta)


class Producto(ABC):
    """Clase abstracta del catálogo.

    Declara precio_final(cantidad) como abstracto: instanciar Producto
    directamente, o una subclase que no lo implemente, falla al
    construir (TypeError propio del mecanismo de ABC), no al usar.
    """

    def __init__(
        self,
        nombre: str,
        precio_base: float,
        stock_cantidad: float,
        categoria_principal: Categoria,
        unidad_venta: UnidadMedida | None = None,
    ) -> None:
        if not nombre or not nombre.strip():
            raise ErrorDominio("El nombre del producto no puede estar vacío.")
        if precio_base < 0:
            raise ErrorDominio("El precio base no puede ser negativo.")
        if stock_cantidad < 0:
            raise ErrorDominio("El stock no puede ser negativo.")
        if not isinstance(categoria_principal, Categoria):
            raise ErrorDominio("La categoría principal debe ser una Categoria.")
        if unidad_venta is not None and not isinstance(unidad_venta, UnidadMedida):
            raise ErrorDominio("La unidad de venta debe ser una UnidadMedida.")

        self._nombre = nombre
        self._precio_base = precio_base
        self._stock_cantidad = stock_cantidad
        self._habilitado = True
        self._unidad_venta = unidad_venta
        self._clasificaciones: list[ProductoCategoria] = []

        # El constructor crea internamente la primera clasificación,
        # con es_principal=True, reutilizando clasificar_en.
        self.clasificar_en(categoria_principal, es_principal=True)

    # Encapsulamiento: properties de solo lectura

    @property
    def nombre(self) -> str:
        return self._nombre

    @property
    def precio_base(self) -> float:
        return self._precio_base

    @property
    def unidad_venta(self) -> UnidadMedida | None:
        return self._unidad_venta

    @property
    def precio_publicado(self) -> str:
        """Estado formateado: '$ 12.50 / kg' o '$ 3.00' si no hay unidad."""
        if self._unidad_venta is not None:
            return f"$ {self._precio_base:.2f} / {self._unidad_venta.simbolo}"
        return f"$ {self._precio_base:.2f}"

    @property
    def disponible(self) -> bool:
        """Estado derivado: habilitado y con stock.

        ProductoCombo redefine esta property (ver esa clase).
        """
        return self._habilitado and self._stock_cantidad > 0

    # Habilitación: única vía para mutar _habilitado

    def habilitar(self) -> None:
        self._habilitado = True

    def deshabilitar(self) -> None:
        self._habilitado = False

    # Composición: Producto fabrica y es dueño de ProductoCategoria

    def clasificar_en(self, categoria: Categoria, es_principal: bool = False) -> None:
        if not isinstance(categoria, Categoria):
            raise ErrorDominio("categoria debe ser una instancia de Categoria.")
        if any(pc.categoria is categoria for pc in self._clasificaciones):
            raise ErrorDominio(
                f"El producto ya está clasificado en '{categoria.nombre}'."
            )
        if es_principal:
            for pc in self._clasificaciones:
                pc._marcar_principal(False)
        nuevo_vinculo = ProductoCategoria(categoria, es_principal)
        self._clasificaciones.append(nuevo_vinculo)

    def categorias(self) -> tuple[ProductoCategoria, ...]:
        """Copia inmutable: nunca la lista interna."""
        return tuple(self._clasificaciones)

    def categoria_principal(self) -> Categoria:
        return next(pc.categoria for pc in self._clasificaciones if pc.es_principal)

    # Contrato Exportable (conformidad estructural, sin heredar)

    def exportar(self) -> str:
        return f"PRD|{self._nombre}|{self.precio_publicado}"

    # Herencia justificada: cada subclase define su propia regla

    @abstractmethod
    def precio_final(self, cantidad: float) -> float:
        """Precio final para la cantidad dada. Regla propia por subclase."""
        raise NotImplementedError

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self._nombre!r})"


# Subclases de venta


def _validar_cantidad_entera(cantidad: float) -> None:
    if not isinstance(cantidad, (int, float)):
        raise ErrorDominio("La cantidad debe ser numérica.")
    if not float(cantidad).is_integer() or cantidad < 1:
        raise ErrorDominio("La cantidad debe ser un valor entero >= 1.")


class ProductoSimple(Producto):
    """Se vende por pieza: precio final = precio base × cantidad (entera)."""

    def precio_final(self, cantidad: float) -> float:
        _validar_cantidad_entera(cantidad)
        return self._precio_base * cantidad


class ProductoPorPeso(Producto):
    """Se vende por peso: admite decimales, redondea a 2 decimales."""

    def precio_final(self, cantidad: float) -> float:
        if not isinstance(cantidad, (int, float)):
            raise ErrorDominio("La cantidad debe ser numérica.")
        if cantidad <= 0:
            raise ErrorDominio("La cantidad debe ser mayor que cero.")
        return round(self._precio_base * cantidad, 2)


class ProductoCombo(Producto):
    """Agrega entre 2 y N productos ya construidos, con descuento.

    Agregación: los componentes se reciben ya construidos y sobreviven
    al combo (el combo no es dueño de su ciclo de vida).

    Decisiones no definidas por el diagrama:
    - precio_base se DERIVA como la suma de los precio_base de sus
      componentes (no es un dato de catálogo propio), y es coherente
      con precio_publicado, que hereda el formateo de Producto.
    - El combo NO tiene stock propio: su disponibilidad se deriva de
      la disponibilidad de sus componentes (además de estar
      habilitado). Por eso redefine la property `disponible`.
    """

    def __init__(
        self,
        nombre: str,
        componentes: list[Producto],
        descuento: float,
        categoria_principal: Categoria,
        unidad_venta: UnidadMedida | None = None,
    ) -> None:
        if not isinstance(componentes, list) or len(componentes) < 2:
            raise ErrorDominio("Un combo necesita al menos 2 componentes.")
        if not all(isinstance(p, Producto) for p in componentes):
            raise ErrorDominio("Todos los componentes deben ser Producto.")
        if not (0 <= descuento < 1):
            raise ErrorDominio("El descuento debe estar en el rango [0, 1).")

        precio_base = sum(p.precio_base for p in componentes)
        super().__init__(
            nombre,
            precio_base,
            stock_cantidad=0,  # sin stock propio: ver `disponible` redefinida
            categoria_principal=categoria_principal,
            unidad_venta=unidad_venta,
        )
        self._componentes: list[Producto] = list(componentes)
        self._descuento = descuento

    def componentes(self) -> tuple[Producto, ...]:
        """Copia inmutable: nunca la lista interna."""
        return tuple(self._componentes)

    @property
    def disponible(self) -> bool:
        return self._habilitado and all(c.disponible for c in self._componentes)

    def precio_final(self, cantidad: float) -> float:
        _validar_cantidad_entera(cantidad)
        suma = sum(c.precio_final(1) for c in self._componentes)
        return suma * (1 - self._descuento) * cantidad


# ProductoDestacado


class ProductoDestacado:
    """Destaca un producto ya existente en la vidriera, con su orden.

    DECISIÓN DE DISEÑO: se REDISEÑA. Deja de ser subclase de Producto.

    Justificación «es-un»: "destacado" no describe una forma distinta
    de vender ni de calcular un precio: no es-un producto con una
    regla propia de precio_final. Es un atributo de EXHIBICIÓN que se
    le agrega a un producto ya construido, sin importar si es
    ProductoSimple, ProductoPorPeso o ProductoCombo. Si se mantuviera
    como subclase, un fiambre destacado tendría que ser a la vez
    ProductoPorPeso Y ProductoDestacado (herencia múltiple forzada), lo
    que es la señal de que el "es-un" no se sostiene.

    Se modela entonces como una clase de asociación (0..* → 1) que
    referencia al Producto que destaca. `_orden_vidriera` vive acá, no
    en Producto. Con este diseño, CUALQUIER producto del catálogo
    (simple, por peso o combo) puede destacarse, sin restricción.
    """

    def __init__(self, producto: Producto, orden_vidriera: int) -> None:
        if not isinstance(producto, Producto):
            raise ErrorDominio("Solo se puede destacar un Producto del catálogo.")
        if orden_vidriera < 0:
            raise ErrorDominio("El orden de vidriera no puede ser negativo.")
        self._producto = producto
        self._orden_vidriera = orden_vidriera

    @property
    def producto(self) -> Producto:
        return self._producto

    @property
    def orden_vidriera(self) -> int:
        return self._orden_vidriera

    def __repr__(self) -> str:
        nombre = self._producto.nombre
        return f"ProductoDestacado({nombre!r}, orden={self._orden_vidriera})"


# Contrato Exportable (Protocol) y exportar_catalogo


class Exportable(Protocol):
    """Contrato estructural: cualquier objeto con exportar() -> str lo cumple.

    Ni Producto ni FichaPuntoDeVenta heredan de esta clase. Producto
    ya tiene el método exportar(); FichaPuntoDeVenta (de un tercero,
    no modificable) también. Ambos conforman el Protocol sin tocarlos.
    """

    def exportar(self) -> str: ...


def exportar_catalogo(items: list[Exportable]) -> list[str]:
    """Exporta en una sola operación productos propios y fichas externas."""
    return [item.exportar() for item in items]
