import requests
import pandas as pd
from requests.auth import HTTPBasicAuth
from concurrent.futures import ThreadPoolExecutor

# ======================================================
# CONFIGURACION
# ======================================================

ORG = "nombre_organizacion"  # Reemplaza con el nombre de tu organización en Azure DevOps
PAT = "acceso_personal_token"  # Reemplaza con tu token de acceso personal (PAT) de Azure DevOps

API_VERSION = "7.1"

auth = HTTPBasicAuth("", PAT)

BASE_URL = f"https://dev.azure.com/{ORG}"

# ======================================================
# CLIENTE
# ======================================================

def get(url):

    try:

        r = requests.get(
            url,
            auth=auth,
            timeout=60
        )

        if r.status_code == 200:
            return r.json()

        return {}

    except Exception as ex:
        print(f"ERROR: {url}")
        print(ex)
        return {}

# ======================================================
# ORGANIZACION
# ======================================================

def get_projects():

    url = (
        f"{BASE_URL}/"
        f"_apis/projects"
        f"?api-version={API_VERSION}"
    )

    data = get(url)

    return data.get("value", [])

# ======================================================
# REPOS
# ======================================================

def get_repositories(project):

    url = (
        f"{BASE_URL}/{project}/"
        f"_apis/git/repositories"
        f"?api-version={API_VERSION}"
    )

    return get(url).get("value", [])

# ======================================================
# PIPELINES
# ======================================================

def get_pipelines(project):

    url = (
        f"{BASE_URL}/{project}/"
        f"_apis/pipelines"
        f"?api-version={API_VERSION}"
    )

    return get(url).get("value", [])

# ======================================================
# SERVICE CONNECTIONS
# ======================================================

def get_service_connections(project):

    url = (
        f"{BASE_URL}/{project}/"
        f"_apis/serviceendpoint/endpoints"
        f"?api-version={API_VERSION}"
    )

    return get(url).get("value", [])

# ======================================================
# ENVIRONMENTS
# ======================================================

def get_environments(project):

    url = (
        f"{BASE_URL}/{project}/"
        f"_apis/distributedtask/environments"
        f"?api-version={API_VERSION}"
    )

    return get(url).get("value", [])

# ======================================================
# VARIABLE GROUPS
# ======================================================

def get_variable_groups(project):

    url = (
        f"{BASE_URL}/{project}/"
        f"_apis/distributedtask/variablegroups"
        f"?api-version={API_VERSION}"
    )

    return get(url).get("value", [])

# ======================================================
# WIKIS
# ======================================================

def get_wikis(project):

    url = (
        f"{BASE_URL}/{project}/"
        f"_apis/wiki/wikis"
        f"?api-version={API_VERSION}"
    )

    return get(url).get("value", [])

# ======================================================
# FEEDS
# ======================================================

def get_feeds(project):

    url = (
        f"https://feeds.dev.azure.com/{ORG}/{project}/"
        f"_apis/packaging/feeds"
        f"?api-version={API_VERSION}"
    )

    return get(url).get("value", [])

# ======================================================
# DASHBOARDS
# ======================================================

def get_dashboards(project):

    url = (
        f"{BASE_URL}/{project}/"
        f"_apis/dashboard/dashboards"
        f"?api-version={API_VERSION}"
    )

    return get(url).get("dashboardEntries", [])

# ======================================================
# AGENT POOLS
# ======================================================

def get_agent_pools():

    url = (
        f"https://dev.azure.com/{ORG}/"
        f"_apis/distributedtask/pools"
        f"?api-version={API_VERSION}"
    )

    return get(url).get("value", [])

# ======================================================
# SCORE DE ADOPCION
# ======================================================

def calculate_score(metrics):

    score = 0

    if metrics["repos"] > 0:
        score += 15

    if metrics["pipelines"] > 0:
        score += 20

    if metrics["service_connections"] > 0:
        score += 10

    if metrics["environments"] > 0:
        score += 10

    if metrics["variable_groups"] > 0:
        score += 10

    if metrics["wikis"] > 0:
        score += 10

    if metrics["feeds"] > 0:
        score += 10

    if metrics["dashboards"] > 0:
        score += 15

    return score

# ======================================================
# ANALISIS PROYECTO
# ======================================================

def analyze_project(project):

    name = project["name"]

    print(f"Analizando: {name}")

    repos = get_repositories(name)
    pipelines = get_pipelines(name)
    svc = get_service_connections(name)
    envs = get_environments(name)
    vars_ = get_variable_groups(name)
    wikis = get_wikis(name)
    feeds = get_feeds(name)
    dashboards = get_dashboards(name)

    metrics = {
        "project": name,
        "repos": len(repos),
        "pipelines": len(pipelines),
        "service_connections": len(svc),
        "environments": len(envs),
        "variable_groups": len(vars_),
        "wikis": len(wikis),
        "feeds": len(feeds),
        "dashboards": len(dashboards)
    }

    metrics["adoption_score"] = calculate_score(metrics)

    return metrics

# ======================================================
# MAIN
# ======================================================

def main():

    projects = get_projects()

    print(f"Proyectos encontrados: {len(projects)}")

    results = []

    with ThreadPoolExecutor(max_workers=10) as executor:

        futures = [
            executor.submit(analyze_project, p)
            for p in projects
        ]

        for f in futures:
            results.append(f.result())

    df = pd.DataFrame(results)

    pools = get_agent_pools()

    pools_df = pd.DataFrame(pools)

    df.to_excel(
        "azure_devops_adoption.xlsx",
        index=False
    )

    pools_df.to_excel(
        "azure_devops_pools.xlsx",
        index=False
    )

    print("Reporte generado")

if __name__ == "__main__":
    main()