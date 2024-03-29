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
public website, using branch `master`:

1. Verify that there are no test failures on the master branch. Check the
'Actions' tab on GitHub to view the test results from the last push event.
1. Determine the version number of the new release.
1. Update the `$version` variable in
[write\_saphon\_php.py](../python/saphon/web/write_saphon_php.py).
1. Create files in `website/intact/en/updates`, `website/intact/es/updates`,
and `website/intact/pt/updates` that list the changes for the new release.
Use the existing files as guidelines for content and format. Review the [commit
history](https://github.com/levmichael/saphon/commits/master) since the last
release was created.
1. Edit the files `website/intact/en/updates.php`,
`website/intact/es/actualizaciones.php`,
and `website/intact/pt/atualizações.php` to include the files created in the
preceding step in the changelog.
1. Commit the changes of the preceding three steps and push to github. If the changes were made directly on github they will be committed already.
1. Publish a prerelease version of the website for testing.
   * Go to the [saphon repo's releases page](https://github.com/levmichael/saphon/releases).
   * Click the 'Draft a new release' button.
   * Click the 'Choose a tag' button and enter the version, e.g. 'v2.1.0'. In the widget click on 'Create new tag: v2.1.0 on publish' option.
   * Enter the version as the title, e.g. 'v2.1.0'.
   * Enter a description.
   * Select the 'This is a pre-release' checkbox.
   * Click the 'Publish release' button.
1. Verify that the publishing action succeeded by reviewing the GitHub
Actions build logs.
1. Review the
['prerelease' website](https://linguistics.berkeley.edu/saphon-prerelease)
by visiting the site in your web browser. Be sure to check that the release
number updated.
  ***If the prerelease is not satisfactory and additional changes are required,
make the needed changes and commit and push to github. Then reset the commit
referenced by the release to the latest commit so that the release includes
your new changes. One way to do that is to delete the existing
release and tag on github, then redo the preceding steps to re-create the new
release, including updating the file contents and version number if it makes
sense. One way to delete the release is to visit the
[releases page](https://github.com/levmichael/saphon/releases), click on the
release name, then click on the 'Delete' button. Next visit the [tags page](https://github.com/levmichael/saphon/tags), click on the corresponding tag name, then click on the 'Delete' button to delete the tag.***
1. If the prerelease website is satisfactory, edit the release on GitHub and
remove the 'pre-release' qualifier. This will trigger the publish action for
the [public website](https://linguistics.berkeley.edu/saphon).

See the file [`.github/workflows/publish_to_webserver.yaml`](../.github/workflows/publish_to_webserver.yaml)
file for details on configuring the publishing action. Several GitHub
secrets must be set in order to provide environment variables used by the
publishing action.
