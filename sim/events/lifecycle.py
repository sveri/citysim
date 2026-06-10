"""
Lifecycle events: aging, birth, death.
German life tables (Statistisches Bundesamt 2021/2023) used for mortality.
Birth probability based on German TFR ~1.46 per woman, distributed over fertile ages.
"""
import random
from datetime import date, timedelta

# Weekly death probability by age bracket (approximated from German Sterbetafel 2020/22)
# Format: (age_from, age_to, weekly_prob_male, weekly_prob_female)
DEATH_TABLE = [
    (0,   1,   0.00080, 0.00060),
    (1,   4,   0.000030, 0.000025),
    (5,   14,  0.000015, 0.000012),
    (15,  24,  0.000060, 0.000025),
    (25,  34,  0.000075, 0.000040),
    (35,  44,  0.000130, 0.000080),
    (45,  54,  0.000280, 0.000170),
    (55,  64,  0.000650, 0.000380),
    (65,  74,  0.001600, 0.000950),
    (75,  84,  0.004500, 0.003000),
    (85,  94,  0.012000, 0.009000),
    (95,  120, 0.030000, 0.025000),
]

# Weekly birth probability per woman aged 15-49 (TFR~1.46, spread over 35 fertile years)
# Simplified: peak at 28-33, tails at 15-19 and 44-49
BIRTH_TABLE = [
    (15, 19, 0.0004),
    (20, 24, 0.0015),
    (25, 29, 0.0028),
    (30, 34, 0.0032),
    (35, 39, 0.0020),
    (40, 44, 0.0007),
    (45, 49, 0.0001),
]

GERMAN_FIRST_NAMES_M = ["Luca", "Noah", "Leon", "Paul", "Felix", "Jonas", "Elias", "Max", "Finn", "Ben"]
GERMAN_FIRST_NAMES_F = ["Emma", "Mia", "Hannah", "Lena", "Lea", "Anna", "Laura", "Sara", "Lisa", "Julia"]
GERMAN_LAST_NAMES = ["Müller", "Schmidt", "Schneider", "Fischer", "Weber", "Meyer", "Wagner", "Becker", "Schulz", "Hoffmann"]


def _weekly_death_prob(age: int, sex: str) -> float:
    for a_from, a_to, pm, pf in DEATH_TABLE:
        if a_from <= age <= a_to:
            return pm if sex == "M" else pf
    return 0.05


def _weekly_birth_prob(age: int) -> float:
    for a_from, a_to, p in BIRTH_TABLE:
        if a_from <= age <= a_to:
            return p
    return 0.0


def age_of(birth_date_str: str, sim_date: date) -> int:
    bd = date.fromisoformat(birth_date_str)
    return (sim_date - bd).days // 365


def process_lifecycle(session, sim_date: date) -> list[dict]:
    """Advance lifecycle for all living people. Returns list of event dicts."""
    from db.schema import Person, Household

    events = []
    people = session.query(Person).filter_by(alive=True).all()

    for person in people:
        age = age_of(person.birth_date, sim_date)
        death_p = _weekly_death_prob(age, person.sex)

        if random.random() < death_p:
            person.alive = False
            events.append({"type": "death", "person_id": person.id,
                           "name": f"{person.first_name} {person.last_name}", "age": age})
            continue

        # Birth: only living women in a household
        if person.sex == "F":
            birth_p = _weekly_birth_prob(age)
            if random.random() < birth_p:
                household = session.get(Household, person.household_id)
                if household:
                    sex = random.choice(["M", "F"])
                    names_m = GERMAN_FIRST_NAMES_M
                    names_f = GERMAN_FIRST_NAMES_F
                    first = random.choice(names_m if sex == "M" else names_f)
                    child = Person(
                        household_id=household.id,
                        first_name=first,
                        last_name=person.last_name,
                        sex=sex,
                        birth_date=sim_date.isoformat(),
                        alive=True,
                    )
                    session.add(child)
                    session.flush()
                    events.append({"type": "birth", "person_id": child.id,
                                   "name": f"{child.first_name} {child.last_name}",
                                   "household_id": household.id})

    session.commit()
    return events
