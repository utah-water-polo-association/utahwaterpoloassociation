from utahwaterpoloassociation.repos import Leagues, get_league


if __name__ == "__main__":
    sha, leauge = get_league(Leagues.UTAH_SPRING_2025)

    for item in leauge.schedule().games:
        print(item.model_dump_json())
