# Notes for developers

The saphon repo contains language data files and related code for building
the saphon public website. The website pages are generated from the data files
and are not part of the repository itself.

## Google Maps API Key

The Google Maps API requires that a developer key be provided when the
javascript library is loaded. The key value is not present in any of the page
templates in the repository. While this key is not private (it is sent in
clear text with every view of the home page), GitHub scans repositories for
various kinds of credentials automatically and sends scary-sounding warnings
if the key is found. To prevent this the key is not present in the repository
itself and is provided as a GitHub secret (found via the repo's Settings page),
and it is interpolated into the page templates when the website is built.

## Manually verifying .yaml content

A test to verify yaml content is in the tests/ subdirectory. To invoke
manually on the current branch:

```bash
cd <repodir>    # where `<repodir>` is the repo base directory
python -m pytest
```

If the test fails, scan the output for errors to correct.

## Automated testing

Every pull\_request to the master branch or push to any branch triggers a
GitHub Action that runs tests automatically. Check the 'Actions' tab on
GitHub to view the results.

See the file [`.github/workflows/run-tests.yaml`](../.github/workflows/run-tests.yaml)
for details on automated testing.

## Release numbering

Releases are named according to the following scheme:

`v{Major}.{Minor}.{Patch}`

TODO: more info on numbering

## Creating a release and publishing the website

A GitHub Action that builds and publishes the public website is
triggered whenever a release is published on GitHub. If the release is marked
as a 'pre-release' the website is created in the prerelease location. Creating
a draft release does not trigger the publishing action.

These are the recommended steps for creating a release and publishing the
public website:

1. Verify that there are no test failures on the master branch. Check the
'Actions' tab on GitHub to view the test results from the last push event.
1. Determine the version number of the new release.
1. Update the `$version` variable in
1. Commit the change of `write_saphon_php.py` and push to github (if not editing directly on github).
[write\_saphon\_php.py](../python/saphon/web/write_saphon_php.py).
1. Create files in `website/intact/en/updates`, `website/intact/es/updates`,
and `website/intact/pt/updates` that list the changes for the new release.
Use the existing files as guidelines for content and format.
1. Edit the files `website/intact/en/updates.php`, `website/intact/es/actualizaciones.php`,
and `website/intact/pt/atualizações.php` to include in the changelog the
files created in the preceding step.
1. Publish a prerelease version of the website for testing. On
GitHub draft a new release and select the 'This is a pre-release' option
before publishing.
1. Verify that the publishing action succeeded by reviewing the GitHub
Actions build logs.
1. Review the 'prerelease' website (saphon/prerelease) by visiting the site
in your web browser.
1. If the prerelease website is satisfactory, edit the release on GitHub
and remove the 'pre-release' qualifier. This will trigger the publish
action for the public website.

See the file [`.github/workflows/publish_to_webserver.yaml`](../.github/workflows/publish_to_webserver.yaml)
file for details on configuring the publishing action. Several GitHub
secrets must be set in order to provide environment variables used by the
publishing action.
