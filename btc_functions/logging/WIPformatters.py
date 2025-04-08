import logging
import os
import datetime
import inspect
from typing import Dict, Any, Optional, Union, List
import json
import colorama
from colorama import Fore, Back, Style

current_dir = os.path.dirname(os.path.abspath(__file__))

logs_dir = os.path.abspath(os.path.join(current_dir, "../../logs"))
os.makedirs(logs_dir, exist_ok=True)
log_file = os.path.join(logs_dir, "logs.log")
fh = logging.FileHandler(log_file)


# Initialize colorama for colored terminal output
colorama.init(autoreset=True)

current_dir = os.path.dirname(os.path.abspath(__file__))

logs_dir = os.path.join(current_dir, "../../logs")
os.makedirs(logs_dir, exist_ok=True)
log_file = os.path.join(logs_dir, "logs.log")
fh = logging.FileHandler(log_file)


class ColoredFormatter(logging.Formatter):
    """Formatter personnalisé pour afficher des logs colorés dans le terminal"""

    COLORS = {
        "DEBUG": Fore.CYAN,
        "INFO": Fore.GREEN,
        "WARNING": Fore.YELLOW,
        "ERROR": Fore.RED,
        "CRITICAL": Fore.RED + Back.WHITE + Style.BRIGHT,
    }

    def format(self, record):
        levelname = record.levelname
        message = super().format(record)
        if levelname in self.COLORS:
            return f"{self.COLORS[levelname]}{message}{Style.RESET_ALL}"
        return message


def setup_logger(
    log_level=logging.INFO, log_rotation_days=7, colored_output=True, json_format=False
):
    """Configuration avancée du logger avec options de rotation et de format

    Args:
        log_level: Niveau de log (default: logging.INFO)
        log_rotation_days: Nombre de jours avant rotation des logs (default: 7)
        colored_output: Activer la coloration des logs en console (default: True)
        json_format: Format JSON pour les logs (utile pour ELK/Splunk) (default: False)
    """
    logger = logging.getLogger()
    logger.setLevel(log_level)

    # Supprimer les handlers existants pour éviter les doublons
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # Date pour le nom du fichier de log
    date_str = datetime.datetime.now().strftime("%Y-%m-%d")
    log_file = os.path.join(logs_dir, f"logs_{date_str}.log")

    # File handler
    if json_format:
        file_formatter = logging.Formatter(
            '{"timestamp":"%(asctime)s", "level":"%(levelname)s", "message":"%(message)s", "module":"%(module)s", "function":"%(funcName)s", "line":"%(lineno)d"}'
        )
    else:
        file_formatter = logging.Formatter(
            "[%(asctime)s] [%(levelname)s] [%(module)s:%(lineno)d] %(message)s"
        )

    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(log_level)
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)

    if colored_output:
        console_formatter = ColoredFormatter("[%(levelname)s] %(message)s")
    else:
        console_formatter = logging.Formatter("[%(levelname)s] %(message)s")

    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # Nettoyage des anciens logs
    cleanup_old_logs(logs_dir, log_rotation_days)

    return logger


def cleanup_old_logs(logs_dir, days_to_keep):
    """Supprime les fichiers de log plus anciens que days_to_keep"""
    now = datetime.datetime.now()
    for filename in os.listdir(logs_dir):
        if filename.startswith("logs_") and filename.endswith(".log"):
            file_path = os.path.join(logs_dir, filename)
            file_time = datetime.datetime.fromtimestamp(os.path.getmtime(file_path))
            if (now - file_time).days > days_to_keep:
                try:
                    os.remove(file_path)
                except Exception:
                    pass


# DECORATIONS AMÉLIORÉES #


def log_title(title: str, style: str = "default") -> str:
    """Crée un titre bien formaté avec plusieurs styles au choix

    Args:
        title: Le titre à afficher
        style: Le style à utiliser ("default", "double", "hash", "equal", "wave")
    """
    styles = {
        "default": ("*", "*", 80),
        "double": ("═", "═", 80),
        "hash": ("#", "#", 80),
        "equal": ("=", "=", 80),
        "wave": ("~", "~", 80),
    }

    char, border_char, length = styles.get(style, styles["default"])
    line = char * length

    return f"\n{line}\n{border_char} {title.center(length - 4)} {border_char}\n{line}\n"


def log_section(title: str, style: str = "default") -> str:
    """Crée une section avec différents styles

    Args:
        title: Le titre de la section
        style: Le style à utiliser ("default", "arrow", "bracket", "dot")
    """
    styles = {
        "default": ("----- ", " ", "-"),
        "arrow": ("---> ", " ", "-"),
        "bracket": ("[ ", " ]", "-"),
        "dot": ("•• ", " ", "·"),
    }

    prefix, suffix, fill_char = styles.get(style, styles["default"])
    remaining_length = 70 - len(title) - len(prefix) - len(suffix)

    return f"\n{prefix}{title}{suffix}{fill_char * remaining_length}\n"


def log_key_value(
    key: str, value: str, key_width: int = 15, colored: bool = False
) -> str:
    """Affiche une paire clé-valeur avec formatage optionnel

    Args:
        key: La clé
        value: La valeur
        key_width: Largeur de la colonne de clé
        colored: Colorer la clé (console uniquement)
    """
    if colored:
        return f"{Fore.BLUE}{key:<{key_width}}{Style.RESET_ALL}: {value}"
    return f"{key:<{key_width}}: {value}"


def log_block(
    header: str, data: Dict[str, Any], style: str = "default", colored: bool = False
) -> str:
    """Crée un bloc de données formaté avec un en-tête

    Args:
        header: L'en-tête du bloc
        data: Dictionnaire de données à afficher
        style: Style du bloc ("default", "json", "compact")
        colored: Colorer les clés (console uniquement)
    """
    if style == "json":
        return json.dumps({header: data}, indent=2)

    if style == "compact":
        lines = [log_title(header, "equal")]
        for k, v in data.items():
            lines.append(f"{k}={v}")
        lines.append("=" * 80)
        return "\n".join(lines)

    # Default style
    lines = [log_title(header)]
    for k, v in data.items():
        lines.append(log_key_value(k, str(v), colored=colored))
    lines.append("*" * 80)
    return "\n".join(lines)


def log_separator(char="-", length=80, style: str = "default") -> str:
    """Crée une ligne de séparation avec différents styles

    Args:
        char: Caractère à utiliser
        length: Longueur totale
        style: Style ("default", "bold", "dotted", "dashed")
    """
    styles = {
        "default": char * length,
        "bold": f"{char * 3} " * (length // 4),
        "dotted": f"{char} " * (length // 2),
        "dashed": f"{char * 3} " * (length // 4),
    }

    return styles.get(style, styles["default"])


def log_table(
    header: List[str], rows: List[List[str]], col_widths: Optional[List[int]] = None
) -> str:
    """Crée un tableau formaté pour les logs

    Args:
        header: Liste des en-têtes de colonnes
        rows: Liste des lignes (chaque ligne est une liste de valeurs)
        col_widths: Liste des largeurs de colonnes (calculé automatiquement si None)
    """
    if not col_widths:
        # Calculer les largeurs de colonnes
        col_widths = []
        for i in range(len(header)):
            width = len(header[i])
            for row in rows:
                if i < len(row):
                    width = max(width, len(str(row[i])))
            col_widths.append(width + 2)  # +2 pour l'espacement

    # Créer la ligne d'en-tête
    header_line = (
        "| " + " | ".join(h.ljust(w - 2) for h, w in zip(header, col_widths)) + " |"
    )
    separator = "+" + "+".join("-" * w for w in col_widths) + "+"

    # Créer les lignes de données
    data_lines = []
    for row in rows:
        padded_row = []
        for i, val in enumerate(row):
            if i < len(col_widths):
                padded_row.append(str(val).ljust(col_widths[i] - 2))
            else:
                padded_row.append(str(val))
        data_lines.append("| " + " | ".join(padded_row) + " |")

    # Assembler le tableau
    table = [separator, header_line, separator]
    table.extend(data_lines)
    table.append(separator)

    return "\n".join(table)


def log_progress(message: str, current: int, total: int, width: int = 40) -> str:
    """Affiche une barre de progression dans les logs

    Args:
        message: Message décrivant l'opération
        current: Valeur actuelle
        total: Valeur totale
        width: Largeur de la barre de progression
    """
    percent = min(100, int(100 * current / total))
    filled_width = int(width * current / total)
    bar = "█" * filled_width + "░" * (width - filled_width)
    return f"{message}: [{bar}] {percent}% ({current}/{total})"


def log_call_info() -> str:
    """Retourne des informations sur la fonction appelante (pour le débogage)"""
    caller = inspect.currentframe().f_back.f_back
    if caller:
        info = inspect.getframeinfo(caller)
        return f"Called from {os.path.basename(info.filename)}:{info.lineno} in {info.function}()"
    return "Call info not available"


def log_timestamp(format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """Retourne un horodatage formaté"""
    return datetime.datetime.now().strftime(format_str)


def log_context(ctx_data: Dict[str, Any]) -> str:
    """Crée un bloc de contexte pour une meilleure traçabilité"""
    caller_info = log_call_info()
    timestamp = log_timestamp()

    ctx_data.update(
        {
            "timestamp": timestamp,
            "caller": caller_info,
        }
    )

    return log_block("EXECUTION CONTEXT", ctx_data, style="default", colored=True)


def create_categorized_logger(category: str):
    """Crée un logger spécifique à une catégorie"""
    logger = logging.getLogger(category)
    return logger
