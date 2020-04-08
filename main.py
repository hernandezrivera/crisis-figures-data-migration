import csv
import urllib.request
import codecs
import yaml
import re

countries = {}  # [term_code]: id, code, name
country_yaml = {}
countries_count = 1

indicators = {}  # [indicator_id]: id, name, organization, country, terms
indicators_yaml = {}
indicators_count = 1

values_yaml = {}  # [value_id]: date, value, source_url, indicator_id
values_count = 1

vocabularies_list = {}  # master vocabularies list for the script

vocabularies_yaml = {}
terms_yaml = {}


def create_machine_name(string_in):
    string = string_in.lower().strip()
    string = re.sub('[^A-Za-z0-9]+', ' ', string)
    string = string.strip().replace(" ", "_")
    while "__" in string:
        string.replace("__", "_")
    return string


def create_new_country(input_line):
    # [term_code]: id, code, name
    global indicators_count

    crisis_index = input_line[0]
    country_code = input_line[2].lower()
    country_name = input_line[1]
    if country_code not in countries:
        countries[country_code] = (indicators_count, crisis_index, country_code, country_name)
        country_yaml["country_" + country_code] = {"code": country_code, "name": country_name}
        indicators_count = indicators_count + 1


def create_vocabularies():
    # to add list of keywords to look for:
    # {("school", "close"), ("school", "not", "function")}
    global vocabularies_list
    vocabularies_list = {
        # term_id : (name, themes, keywords)
        "term_acutely_malnourished_children": ("Acutely malnourished children", {"Nutrition"}, {("child", "maln")}),
        "term_acutely_malnourished_pregnant_women": (
            "Pregnant or Lactating Acutely Malnourished Women", {"Nutrition"}, {("pregnan", "maln")}),

        "term_children_in_need": (
            "Children in need", {"Protection and Human Rights"}, {("child", "need"), ("child", "")}),
        "term_people_in_need": ("People in need", {"Protection and Human Rights"}, {("people", "need")}),
        "term_people_targeted_for_assistance": (
            "People targeted for assistance", {"Protection and Human Rights"}, {("people", "target")}),
        "term_refugees": (
            "Refugess", {"Protection and Human Rights", "Displacement"}, {("ref", ""), ("asylum", "seek")}),
        "term_returnees": ("Returness", {"Protection and Human Rights", "Displacement"}, {("ret", "")}),
        "term_idps": ("IDPs", {"Protection and Human Rights", "Displacement"}, {("idp", ""), ("displace", "")}),

        "term_humanitarian_access_incidents": (
            "Humanitarian acess incidents", {"Safety and Security"}, {("access", "incident")}),
        "term_security_incidents": ("Security incidents", {"Safety and Security"}, {("secur", "incident")}),
        "term_civilians_attacks": ("Civilians - Attacks", {"Safety and Security"}, {("civ", "attack")}),
        "term_civilians_incidents": ("Civilians - Incidents", {"Safety and Security"}, {("civ", "incident")}),
        "term_civilians_killed": ("Civilians - Killed", {"Safety and Security"}, {("civ", "kill")}),
        "term_civilians_injured": ("Civilians - Injured", {"Safety and Security"}, {("civ", "injur")}),
        # Killed and Injured  + Injured and Injuries

        "term_civilians_deaths": ("Civilians - Deaths", {"Safety and Security"}, {("civ", "death"), ("civ", "dead"), }),
        "term_aid_workers_kka_incidents": (
            "Aid workers - KKA incidents", {"Safety and Security"}, {("aid", "work", "kka")}),
        "term_aid_workers_arrested": ("Aid workers - Arrested", {"Safety and Security"}, {("aid", "work", "arrest")}),
        "term_aid_workers_kidnapped": ("Aid workers - Kidnapped", {"Safety and Security"}, {("aid", "work", "kidnap")}),
        "term_aid_workers_killed": ("Aid workers - Killed", {"Safety and Security"}, {("aid", "work", "kill")}),

        "term_health_facilities_injuries": (
            "Health facilities - Injuries", {"Safety and Security", "Health"}, {("health", "facilit", "injur")}),
        "term_health_facilities_kill": (
            "Health facilities - Killed", {"Safety and Security", "Health"}, {("health", "facilit", "kill")}),
        "term_health_facilities_attacks": (
            "Health facilities - Attacks", {"Safety and Security", "Health"},
            {("health", "facilit", "attack"), ("health", "care", "attack")}),
        "term_health_facilities_closed": (
            "Health facilities - Closed", {"Health"}, {("health", "facilit", "close"), ("health", "centre", "close")}),
        "term_cholera_cases": ("Cholera cases", {"Health", "Cholera", "Disease cases"}, {("cholera", "case")}),
        "term_cholera_deaths": ("Cholera deaths", {"Health", "Cholera", "Disease deaths"}, {("cholera", "death")}),
        "term_ebola_cases": ("Ebola cases", {"Health", "Ebola", "Disease cases"}, {("ebola", "case")}),
        "term_ebola_deaths": ("Ebola deaths", {"Health", "Ebola", "Disease deaths"}, {("ebola", "death")}),
        "term_lassa_fever_cases": (
            "Lassa fever cases", {"Health", "Lassa fever", "Disease cases"}, {("lassa", "case")}),
        "term_lassa_fever_deaths": (
            "Lassa fever deaths", {"Health", "Lassa fever", "Disease deaths"}, {("lassa", "death")}),
        "term_malaria_cases": ("Malaria cases", {"Health", "Malaria", "Disease cases"}, {("malaria", "case")}),
        "term_malaria_deaths": ("Malaria deaths", {"Health", "Malaria", "Disease deaths"}, {("malaria", "death")}),
        "term_measles_cases": ("Measles cases", {"Health", "Measles", "Disease cases"}, {("measles", "case")}),
        "term_measles_deaths": ("Measles deaths", {"Health", "Measles", "Disease deaths"}, {("measles", "death")}),
        "term_yellow_fever_cases": (
            "Yellow fever cases", {"Health", "Yellow fever", "Disease cases"}, {("yellow", "case")}),
        "term_yellow_fever_deaths": (
            "Yellow fever deaths", {"Health", "Yellow fever", "Disease deaths"}, {("yellow", "death")}),

        "term_schools_closed": ("Schools - Closed", {"Education"}, {("school", "close")}),
        "term_schools_damaged": ("Schools - Damaged", {"Education"}, {("school", "damage")}),
        "term_students_affected_by_closure_of_schools": ("Students affected", {"Education"}, {("student", "closure")}),

        "term_food_insecure_people": (
            "Food insecure people", {"Food"}, {("food", "insecur"), ("people", "food", "crisis"), ("ipc", "3")}),
        "term_people_assisted_wfp": ("People assisted - WFP", {"Food"}, {("assist", "wfp")})
    }

    global vocabularies_yaml
    global terms_yaml

    vocabularies_yaml["vocabulary_base_indicator"] = {"name": "base_indicator", "label": "Base Indicator"}
    vocabularies_yaml["vocabulary_theme"] = {"name": "theme", "label": "Theme"}

    # Build list of tags and themes
    for item in vocabularies_list.items():
        tag_ref = item[0]
        tag_name = item[1][0].strip()
        tag_machine_name = create_machine_name(tag_name)
        tag_themes = item[1][1]
        tag_keywords = item[1][2]
        tag_themes_ref = []

        for theme in tag_themes:
            theme_name = theme
            theme_machine_name = create_machine_name(theme_name)
            theme_ref = "term_theme_" + theme_machine_name
            if terms_yaml.get(theme_ref, "") == "":
                terms_yaml[theme_ref] = {"name": theme_machine_name, "label": theme_name,
                                         "vocabulary": "@vocabulary_theme", }
            tag_themes_ref.append("@" + theme_ref)

        terms_yaml[tag_ref] = {"name": tag_machine_name,
                               "label": tag_name,
                               "vocabulary": "@vocabulary_base_indicator",
                               "parent": tag_themes_ref
                               }

    return vocabularies_list


def search_country_ref(country_code):
    for country_ref in country_yaml:
        for country_data in country_yaml[country_ref].items():
            if country_code in country_data:
                return country_ref
    return None


def search_terms_ref(theme_name):
    for terms_ref in terms_yaml:
        for terms_data in terms_yaml[terms_ref].items():
            if theme_name in terms_data:
                return terms_ref
    return None


def assign_terms(indicator_name):
    indicator_terms = []

    indicator_name = indicator_name.lower()
    for tag in vocabularies_list.items():
        tag_ref = tag[0]
        tag_name = tag[1][0]
        tag_themes = tag[1][1]
        tag_keywords = tag[1][2]

        matching_tag = False
        for element in tag_keywords:
            matching_element = True
            for word in element:
                matching_element = (word in indicator_name) & matching_element
            matching_tag = matching_tag | matching_element
        if matching_tag:
            indicator_terms.append('@' + tag_ref)
            for theme in tag_themes:
                theme_ref = search_terms_ref(theme)
                if '@' + theme_ref not in indicator_terms:
                    indicator_terms.append('@' + theme_ref)

    return indicator_terms


def create_new_indicator(input_line):
    # [indicator_id]: id, name, organization, country, terms
    global indicators_count
    global indicators_yaml

    indicator_name = input_line[3].strip()
    indicator_source = input_line[4].strip()
    country_code = input_line[2].strip().lower()
    country_ref = search_country_ref(country_code)
    indicator_machine_name = create_machine_name(indicator_name)
    indicator_ref = country_code + "-" + indicator_machine_name
    if indicator_ref not in indicators:
        if indicators_count == 156:  ## line for debugging individual indicators
            b = False
        terms = assign_terms(indicator_name)
        indicators[indicator_ref] = (
            indicators_count, indicator_name, indicator_source, country_code, terms)
        indicators_yaml[indicator_ref] = \
            {'name': indicator_name,
             'organization': indicator_source,
             'country': '@' + country_ref,
             'terms': terms
             }
        indicators_count = indicators_count + 1
    return indicator_ref


def create_new_value(input_line, indicator_ref_in):
    # [value_id]: date, value, source_url, indicator_id
    global values_count

    value_date = input_line[6]
    value_figure = input_line[5]
    value_url = input_line[7]

    values_yaml[indicator_ref_in + '-' + str(values_count)] = {'value': int(value_figure),
                                                               'date': r"<(\DateTime::createFromFormat('Y-m-d', '" + value_date + r"'))>",
                                                               'sourceURL': str(value_url) + '',
                                                               'indicator': '@' + indicator_ref_in}
    values_count = values_count + 1


# BEGIN OF MAIN

url = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vRMmUaCgM3NZHrHpewmiXQvPGJDy6dYQOFx1Of6TLxP4NgGHqTLVhwNcvVeVrEBRxo4E6JlGpPxcXhd/pub?gid=2128440595&single=true&output=csv'
# ['crisis_index', 'crisis_name', 'crisis_iso3', 'figure_name', 'figure_source', 'figure_value', 'figure_date', 'figure_url']
# 0 > 'crisis_index'
# 1 > 'crisis_name'
# 2 > 'crisis_iso3'
# 3 > 'figure_name'
# 4 > 'figure_source'
# 5 > 'figure_value'
# 6 > 'figure_date'
# 7 > 'figure_url'
print("DEBUG: Starting")
ftpstream = urllib.request.urlopen(url)
print("DEBUG: Just opened URL")
csvfile = csv.reader(codecs.iterdecode(ftpstream, 'utf-8'))
print("DEBUG: Just got the CSV file")

vocabularies_list = create_vocabularies()

# skip headers and print
print(next(csvfile))

# for i in range(1000):
#    line = next(csvfile)
for line in csvfile:
    create_new_country(line)
    indicator_reference = create_new_indicator(line)
    create_new_value(line, indicator_reference)

# for debugging indicators with no theme
for item in indicators:
    value = indicators[item]
    if not value[4]:
        # print (value)
        foo = False

with open('010-country.yaml', 'w') as f:
    country_yaml = {"App\Entity\Country": country_yaml}
    countries_str = yaml.dump(country_yaml, explicit_start=False, explicit_end=False, default_flow_style=False,
                              default_style='', indent=4)
    f.write(countries_str)

with open('020-vocabulary.yaml', 'w') as f:
    vocabularies_yaml = {"App\Entity\Vocabulary": vocabularies_yaml}
    vocabularies_str = yaml.dump(vocabularies_yaml, explicit_start=False, explicit_end=False, default_flow_style=False,
                                 default_style='', indent=4)
    f.write(vocabularies_str)

with open('030-term.yaml', 'w') as f:
    terms_yaml = {"App\Entity\Term": terms_yaml}
    terms_str = yaml.dump(terms_yaml, explicit_start=False, explicit_end=False, default_flow_style=False,
                          default_style='', indent=4)
    f.write(terms_str)

with open('040-indicator.yaml', 'w') as f:
    indicators_yaml = {"App\Entity\Indicator": indicators_yaml}
    indicators_str = yaml.dump(indicators_yaml, explicit_start=False, explicit_end=False, default_flow_style=False,
                               default_style='', indent=4)
    f.write(indicators_str)

with open('050-indicator_value.yaml', 'w') as f:
    values_yaml = {"App\Entity\IIndicatorValue": values_yaml}
    values_str = yaml.dump(values_yaml, explicit_start=False, explicit_end=False, default_flow_style=False,
                           default_style='', indent=4)
    f.write(values_str)
