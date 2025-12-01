# orient_ai.py
#
# Prototype simple pour "OrientAI"
# - Collecte un profil élève
# - Compare avec quelques programmes d'exemple
# - Donne les meilleures recommandations

from dataclasses import dataclass
from typing import Dict, List, Tuple

@dataclass
class StudentProfile:
    """
    Profil d'un élève de lycée.
    - grades : notes par matière (0 à 20)
    - interests : centres d'intérêt (mots-clés en minuscules)
    - aspirations : idées de métiers / domaines visés
    """
    name: str
    grades: Dict[str, float]
    interests: List[str]
    aspirations: List[str]


@dataclass
class Program:
    """
    Représente une filière / un parcours / une école.
    - min_grades : notes minimales recommandées par matière
    - tags : mots-clés décrivant la filière
    """
    id: str
    name: str
    domain: str
    min_grades: Dict[str, float]
    tags: List[str]

    def score_for(self, student: StudentProfile) -> float:
        """
        Calcule un score d'adéquation entre 0 et 1.
        Basé sur :
        - la différence entre les notes de l'élève et les notes minimales
        - les intérêts communs
        - la correspondance avec ses aspirations
        """

        if not self.min_grades:
            grade_score = 0.0
        else:
            scores = []
            for subject, required_grade in self.min_grades.items():
                student_grade = student.grades.get(subject, 0.0)

                diff = student_grade - required_grade

                normalized = 0.5 + diff / 10.0
                normalized = max(0.0, min(1.0, normalized))
                scores.append(normalized)

            grade_score = sum(scores) / len(scores)

        common_tags = set(self.tags) & set(student.interests)
        if self.tags:
            interest_score = len(common_tags) / len(self.tags)
        else:
            interest_score = 0.0

        common_aspirations = set(self.tags) & set(student.aspirations)
        aspiration_score = 1.0 if common_aspirations else 0.0

        final_score = 0.6 * grade_score + 0.25 * interest_score + 0.15 * aspiration_score
        return final_score

def recommend_programs(student: StudentProfile,
                    programs: List[Program],
                    top_k: int = 3) -> List[Tuple[Program, float]]:
    """
    Retourne les top_k meilleurs programmes avec leur score.
    """
    scored: List[Tuple[Program, float]] = []
    for p in programs:
        s = p.score_for(student)
        scored.append((p, s))

    scored.sort(key=lambda x: x[1], reverse=True)
    return scored[:top_k]

def build_example_programs() -> List[Program]:
    """
    Quelques programmes d'exemple.
    À remplacer / compléter par vos vraies filières.
    """
    return [
        Program(
            id="ing_info",
            name="Cycle Prépa + Ingénieur Informatique",
            domain="Informatique",
            min_grades={"maths": 14, "physique": 12, "francais": 10},
            tags=["informatique", "programmation", "algorithmes", "intelligence artificielle"]
        ),
        Program(
            id="medecine",
            name="Médecine",
            domain="Santé",
            min_grades={"maths": 12, "physique": 13, "svt": 15, "francais": 12},
            tags=["santé", "biologie", "contact humain", "hôpital"]
        ),
        Program(
            id="eco_gestion",
            name="Économie & Gestion",
            domain="Business",
            min_grades={"maths": 11, "francais": 12, "philo": 10},
            tags=["économie", "management", "entrepreneuriat", "finance"]
        ),
        Program(
            id="lettres",
            name="Lettres & Sciences Humaines",
            domain="Lettres",
            min_grades={"francais": 14, "philo": 13, "langues": 14},
            tags=["littérature", "philosophie", "langues", "écriture"]
        )
    ]

def ask_float(prompt: str) -> float:
    """
    Demande un nombre à l'utilisateur, avec re-saisie en cas d'erreur.
    """
    while True:
        value = input(prompt).strip()
        try:
            return float(value.replace(",", "."))
        except ValueError:
            print("Veuillez entrer un nombre valide.")


def ask_list(prompt: str) -> List[str]:
    """
    Demande une liste de mots séparés par des virgules.
    """
    raw = input(prompt).strip().lower()
    if not raw:
        return []
    return [item.strip() for item in raw.split(",") if item.strip()]


def collect_student_profile() -> StudentProfile:
    """
    Pose quelques questions pour construire le profil de l'élève.
    """
    print("=== ORIENTAI : PROFIL ÉLÈVE ===")
    name = input("Nom de l'élève : ").strip()

    subjects = ["maths", "physique", "svt", "francais", "philo", "langues"]
    grades: Dict[str, float] = {}
    print("\nEntrez les notes de l'élève (0 à 20). Laissez vide si pas de note :")
    for subject in subjects:
        raw = input(f"- {subject} : ").strip()
        if raw == "":
            continue
        try:
            grade = float(raw.replace(",", "."))
            grades[subject] = grade
        except ValueError:
            print("Valeur invalide, note ignorée pour cette matière.")

    interests = ask_list(
        "\nCentres d'intérêt (informatique, biologie, économie, arts, etc.) "
        "\nPréfèrence: "
    )

    aspirations = ask_list(
        "\nIdées de métiers / domaines visés (ingénieur, médecin, enseignant, etc.) "
        "\nPréfèrence : "
    )

    return StudentProfile(
        name=name,
        grades=grades,
        interests=interests,
        aspirations=aspirations
    )


def main() -> None:
    programs = build_example_programs()
    student = collect_student_profile()

    print("\n=== CALCUL DES RECOMMANDATIONS ===")
    recommendations = recommend_programs(student, programs, top_k=3)

    print(f"\nMeilleures recommandations pour {student.name} :\n")
    for prog, score in recommendations:
        print(f"- {prog.name} ({prog.domain})")
        print(f"  Score d'adéquation : {score:.2f}")
        print(f"  Tags : {', '.join(prog.tags)}\n")


if __name__ == "__main__":
    main()