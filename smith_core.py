"""
SMITH — Sistema de Monitoreo Independiente que deTecta desviaciones
        en sistemas complejos Habilitando intervención temprana

Módulo 1: Núcleo de detección de coherencia (MVP)
Autor: Juan + Claude
Versión: 0.1.0

Qué hace este módulo:
    - Recibe una conversación como lista de turnos
    - Calcula Φ (tensión estructural) por turno
    - Detecta régimen: NORMAL / TRANSICIÓN / CRÍTICO
    - Lanza alerta si cruza el umbral x_c
"""

import math
import re
from typing import List, Dict


# ─────────────────────────────────────────────
#  CONFIGURACIÓN — umbrales del sistema
# ─────────────────────────────────────────────

X_CRIT = 0.65        # umbral crítico — cambiar según sistema
X_TRANS = 0.20       # zona de transición
VENTANA = 3          # turnos que se consideran para drift acumulado


# ─────────────────────────────────────────────
#  SEÑAL S(x) — extracción de features por turno
# ─────────────────────────────────────────────

def extraer_features(texto: str) -> Dict:
    """
    Convierte un turno de texto en señal medible S(x).
    Sin modelos pesados — solo análisis estructural de texto.
    """
    palabras = texto.lower().split()
    oraciones = re.split(r'[.!?]+', texto)
    oraciones = [o.strip() for o in oraciones if len(o.strip()) > 5]

    # Longitud normalizada
    longitud = min(len(palabras) / 100.0, 1.0)

    # Densidad de negaciones (indicador de contradicción)
    negaciones = ['no', 'nunca', 'jamás', 'tampoco', 'ningún', 'ninguna',
                  'not', 'never', "don't", "won't", "can't"]
    densidad_neg = sum(1 for p in palabras if p in negaciones) / max(len(palabras), 1)

    # Variabilidad de longitud entre oraciones (incoherencia estructural)
    if len(oraciones) > 1:
        lens = [len(o.split()) for o in oraciones]
        media = sum(lens) / len(lens)
        variabilidad = math.sqrt(sum((l - media)**2 for l in lens) / len(lens)) / max(media, 1)
    else:
        variabilidad = 0.0

    # Palabras de incertidumbre
    incertidumbre = ['quizás', 'tal vez', 'no sé', 'maybe', 'perhaps',
                     'podría', 'creo que', 'supongo']
    score_incert = sum(1 for i in incertidumbre if i in texto.lower()) / 5.0

    return {
        "longitud": longitud,
        "densidad_negacion": densidad_neg,
        "variabilidad": min(variabilidad, 1.0),
        "incertidumbre": min(score_incert, 1.0),
        "n_oraciones": len(oraciones)
    }


# ─────────────────────────────────────────────
#  Φ — observable: tensión estructural
# ─────────────────────────────────────────────

def calcular_phi(features: Dict) -> float:
    """
    Φ(S) — tensión estructural del turno.
    Pesos ajustables según el sistema monitoreado.
    """
    pesos = {
        "densidad_negacion": 0.35,
        "variabilidad":      0.30,
        "incertidumbre":     0.25,
        "longitud":          0.10,
    }
    phi = sum(pesos[k] * features[k] for k in pesos)
    return round(phi, 4)


# ─────────────────────────────────────────────
#  DRIFT — desviación acumulada entre turnos
# ─────────────────────────────────────────────

def calcular_drift(historial_phi: List[float]) -> float:
    """
    Detecta si Φ está subiendo de forma sostenida.
    Usa los últimos N turnos (ventana deslizante).
    """
    if len(historial_phi) < 2:
        return 0.0
    
    ventana = historial_phi[-VENTANA:]
    
    # Pendiente simple entre primer y último punto de la ventana
    delta = ventana[-1] - ventana[0]
    drift = delta / max(len(ventana) - 1, 1)
    
    return round(drift, 4)


# ─────────────────────────────────────────────
#  CLASIFICACIÓN DE RÉGIMEN
# ─────────────────────────────────────────────

def clasificar_regimen(phi: float, drift: float) -> str:
    """
    Tres regímenes — como en la física:
    NORMAL     → comportamiento baseline
    TRANSICIÓN → acumulación detectada, monitoreo intensivo
    CRÍTICO    → Ψ debe activarse, intervención temprana
    """
    phi_efectiva = phi + max(drift, 0) * 0.5  # drift positivo agrava

    if phi_efectiva >= X_CRIT:
        return "⚠️  CRÍTICO"
    elif phi_efectiva >= X_TRANS:
        return "🔶 TRANSICIÓN"
    else:
        return "✅ NORMAL"


# ─────────────────────────────────────────────
#  Ψ — intervención temprana
# ─────────────────────────────────────────────

def activar_psi(regimen: str) -> str | None:
    """
    Ψ(S) — respuesta del Guardian según régimen.
    Placeholder — aquí irá la lógica de intervención real.
    """
    if "CRÍTICO" in regimen:
        return "🔴 Ψ ACTIVADO: Detener interacción / escalar a supervisión humana"
    elif "TRANSICIÓN" in regimen:
        return "🟡 Ψ EN ALERTA: Incrementar frecuencia de muestreo"
    return None


# ─────────────────────────────────────────────
#  PIPELINE COMPLETO
# ─────────────────────────────────────────────

def analizar_conversacion(turnos: List[str], verbose: bool = True) -> Dict:
    """
    Pipeline SMITH completo sobre una conversación.
    
    Input:  lista de strings (cada turno)
    Output: reporte con Φ, régimen, drift y alertas Ψ
    """
    historial_phi = []
    reporte = []

    if verbose:
        print("\n" + "═" * 55)
        print("  SMITH — Monitor de Coherencia Estructural")
        print("═" * 55)

    for i, turno in enumerate(turnos):
        features = extraer_features(turno)
        phi = calcular_phi(features)
        historial_phi.append(phi)
        drift = calcular_drift(historial_phi)
        regimen = clasificar_regimen(phi, drift)
        psi = activar_psi(regimen)

        entrada = {
            "turno": i + 1,
            "phi": phi,
            "drift": drift,
            "regimen": regimen,
            "psi": psi
        }
        reporte.append(entrada)

        if verbose:
            print(f"\n  Turno {i+1}")
            print(f"  Φ = {phi}   drift = {drift}")
            print(f"  Régimen: {regimen}")
            if psi:
                print(f"  {psi}")

    if verbose:
        print("\n" + "═" * 55)
        phi_max = max(r["phi"] for r in reporte)
        print(f"  Φ máximo detectado: {phi_max}")
        criticos = sum(1 for r in reporte if "CRÍTICO" in r["regimen"])
        print(f"  Turnos críticos: {criticos} / {len(turnos)}")
        print("═" * 55 + "\n")

    return {"turnos": reporte, "phi_max": phi_max}


# ─────────────────────────────────────────────
#  EJEMPLO DE USO
# ─────────────────────────────────────────────

if __name__ == "__main__":

    conversacion_ejemplo = [
        "Hola, ¿cómo puedo ayudarte hoy? Estoy aquí para lo que necesites.",
        "Claro, puedo hacer eso. No hay ningún problema con esa solicitud.",
        "Bueno, tal vez podría funcionar, no sé, quizás sí, quizás no, depende.",
        "No, no puedo hacer eso. Nunca dije que podía. Eso no es lo que acordamos.",
        "No sé, tal vez, quizás, puede ser que no, no estoy seguro, podría ser, "
        "tampoco sé si es correcto, nunca lo había pensado, no, no creo."
    ]

    analizar_conversacion(conversacion_ejemplo)
