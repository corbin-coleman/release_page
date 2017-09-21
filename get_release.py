import requests
from flask import Flask, render_template
from datetime import datetime, timedelta
from os import environ
app = Flask(__name__)

ALL_RELEASES = []

token = environ.get('GIT_AUTH_TOKEN')
headers = {'Authorization': 'token {:s}'.format(token)}

def get_releases_from_file():
    new_releases = []

    projects_file = environ.get('PROJECTS_FILE')
    with open(projects_file, 'r') as docker_projects:
        for project in docker_projects:
            owner_and_repo = project.strip('\n').split('/')
            owner = owner_and_repo[0]
            repo = owner_and_repo[1]
            releases = requests.get('https://api.github.com/repos/{:s}/{:s}/releases'.format(owner, repo), headers=headers)
            latest_found = 0
            prerelease_found = 0
            next_candidate = ('WIP', '')
            latest_release = ('WIP', '')

            for release in releases.json():
                potential_release = (release['tag_name'], release['html_url'])
                if latest_found == 0:
                    if release['prerelease'] is True and prerelease_found == 0:
                        prerelease_found = 1
                        next_candidate = potential_release
                    elif release['prerelease'] is False:
                        latest_found = 1
                        latest_release = potential_release
                else:
                    break
            
            github_repo = "{:s}/{:s}".format(owner, repo)
            repo_url = 'https://github.com/{:s}'.format(github_repo)
            repo_info = (github_repo, repo_url)
            full_release = (repo_info, latest_release, next_candidate)
            new_releases.append(full_release)
    ALL_RELEASES.append(new_releases)

@app.route("/")
def release_page():
    format = "%a %b %d %H:%M:%S %Y"
    two_hours = timedelta(hours=2)
    current_time = datetime.now()
    if (current_time - release_page.last_updated) >= two_hours:
        get_releases_from_file()
        release_page.last_updated = current_time
    updated_at = release_page.last_updated.strftime(format)
    if len(ALL_RELEASES) > 0:
        release_page.all_releases = ALL_RELEASES.pop(0)
    all_releases = release_page.all_releases
    return render_template('release_page.html', all_releases=all_releases, updated_at=updated_at)

if __name__ == '__main__':
    get_releases_from_file()
    release_page.all_releases = ALL_RELEASES.pop(0)
    release_page.last_updated = datetime.now()
    app.run(host='0.0.0.0')
