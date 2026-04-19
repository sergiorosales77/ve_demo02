Para poder realizar el cambio sin validación de coordinación de dirección general, es necesario seguir los siguientes pasos:
1. Se determina como redundante el paso de la validación de coordinación de dirección general, ya que no aporta valor al proceso y puede ser omitido sin afectar la calidad del resultado final.
2. Se actualiza el procedimiento para eliminar la validación de coordinación de dirección general, asegurando que el proceso siga siendo eficiente y efectivo.
3. Se requiere hacer ajustes en el desarrollo de la aplicación SPIN TecNM, para que el proceso de cambio se realice sin la necesidad de esta validación, garantizando que el sistema funcione correctamente y cumpla con los requisitos establecidos.
Se requiere una validación en el sistma y realizar un plan para implementar el cambio sin la validación de coordinación de dirección general, asegurando que el proceso se realice de manera ordenada y sin contratiempos.
Actualment funciona de la siguiente manera:
  1. El cambio va de P006 Solicita Autorización de DG(Coordinador de Centro de Trabajo) -> P007 Valida Trámite ( Coordinación de Dirección General).
  2. P007 Valida Trámite  Positivo( Coordinación de Dirección General) -> P008 Tramita pago ante IMPI (Coordinador Centro de Trabajo). 
  3. P007 Valida Trámite Negativo ( Coordinación de Dirección General) -> P07A Rechaza Trámite (Coordinador Centro de Trabajo).
  4. P07A Valida Rechazo (Es posible corregir el Tramite) -> P005 Corrige solicitud (Solicitante).
  5. P07A Valida Rechazo (No es posible corregir el Tramite) -> P07B Termina trámite (Coordinación de Coordinador de CT).


El cambio propuesto es el siguiente:
  1. El cambio va de P006 Valida trámite Positivo (Coordinador de Centro de Trabajo) -> P008 Tramita pago de solicitud ante IMPI(Apoderado Legal).
  2. P006 Valida trámite Negativo con posibilidad de corregir por solicitante (Coordinador de Centro de Trabajo) -> P005 Corrige solicitud (Solicitante).
  3. P006 Valida trámite Negativo sin posibilidad de corregir por solicitante (Coordinador de Centro de Trabajo) -> P007 Termina trámite (Coordinación de Coordinador de CT).


Templates huérfanos identificados: autorizacion_tramite_detalle.html, seguimiento_p07a_list.html y seguimiento_p07a_detalle.html