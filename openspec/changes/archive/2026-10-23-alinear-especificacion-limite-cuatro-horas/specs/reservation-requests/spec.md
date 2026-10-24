# Spec Delta: Solicitudes de reserva

## MODIFIED Requirements

### Requirement: RF-04.2 Validez temporal de la solicitud
El sistema SHALL aceptar únicamente intervalos con inicio estrictamente futuro, fin posterior, un solo día en `America/Bogota`, precisión de minutos con segundos en cero y duración máxima de cuatro horas consecutivas. No SHALL exigir anticipación mínima adicional ni horizonte máximo. Relación: Plan 1.6, 2.4, 6.7, riesgo R-07 y RF-04.6.

#### Scenario: Intervalo futuro válido
- **GIVEN** un inicio futuro y un fin posterior en el mismo día institucional
- **WHEN** se valida la solicitud
- **THEN** el intervalo supera la validación temporal

#### Scenario: Inicio no futuro
- **GIVEN** un inicio igual o anterior al instante actual institucional
- **WHEN** se valida la solicitud
- **THEN** el sistema rechaza el intervalo sin crear la solicitud

#### Scenario: Inicio futuro sin anticipación adicional
- **GIVEN** un inicio posterior al instante actual que cumple las demás reglas
- **WHEN** se valida la solicitud
- **THEN** el sistema no la rechaza por carecer de un margen mínimo adicional

#### Scenario: Fin no posterior
- **GIVEN** un fin igual o anterior al inicio
- **WHEN** se valida la solicitud
- **THEN** el sistema rechaza el intervalo sin crear la solicitud

#### Scenario: Intervalo entre días distintos
- **GIVEN** un inicio y un fin que pertenecen a días calendario distintos en la zona institucional
- **WHEN** se valida la solicitud
- **THEN** el sistema la rechaza porque la primera versión admite reservas de un solo día

#### Scenario: Segundos distintos de cero
- **GIVEN** un inicio o fin con segundos distintos de cero
- **WHEN** se valida la solicitud
- **THEN** el sistema rechaza el intervalo e indica que la precisión permitida es de minutos

#### Scenario: Fecha futura sin horizonte máximo
- **GIVEN** un intervalo futuro que cumple las demás reglas
- **WHEN** se valida la solicitud
- **THEN** el sistema no lo rechaza únicamente por la distancia entre la fecha actual y la fecha solicitada

#### Scenario: Duración exactamente de cuatro horas
- **GIVEN** una solicitud de exactamente cuatro horas que cumple las demás reglas
- **WHEN** se valida la duración
- **THEN** el sistema no la rechaza por duración

#### Scenario: Duración extensa dentro del mismo día
- **GIVEN** una solicitud de 09:00 a 15:00 contenida en el horario habilitado y sin conflictos aprobados
- **WHEN** se valida la duración
- **THEN** el sistema rechaza la solicitud e informa el límite máximo de cuatro horas consecutivas
