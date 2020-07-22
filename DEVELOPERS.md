# Notes for developers

The saphon repo contains language data files and related code for building
the saphon public website. The website pages are generated from the data files
and are not part of the repository itself.

## Verifying .yaml content

A test to verify yaml content is in the tests/ subdirectory. To invoke
manually on the current branch:

1. `cd <repodir>`    # where `<repodir>` is the repo base directory
1. `python -m pytest`
1. If the test fails, scan the output for errors to correct.

## Automated testing

Every pull\_request to the master branch or push to any branch triggers a
GitHub Action that runs tests automatically. Check the 'Actions' tab on
GitHub to view the results.

See the file `.github/workflows/run-tests.yaml` for details on automated
testing.

## Release numbering

Releases are named according to the following scheme:

`v{Major}.{Minor}.{Patch}`

## Publishing

There is a GitHub Action that builds and publishes the public website that is
triggered whenever a release is published. If the release is marked as a
'pre-release' the website is created in the prerelease location. Creating a
draft release does not trigger the publishing action until the release is
published.

These are the recommended steps for publishing the public website:

1. Verify that there are no test failures on the master branch. Check the
'Actions' tab on GitHub to view the test results from the last push event.
1. Publish a prerelease version of the website for testing. On
GitHub draft a new release and select the 'This is a pre-release' option
before publishing.
1. Verify that the publishing action succeeded by reviewing the GitHub
Actions build logs.
1. Review the 'prerelease' website (saphon/prerelease).
1. If the prerelease website is satisfactory, edit the release on GitHub
and remove the 'pre-release' qualifier. This will trigger the publish
action for the public website.

See the file `.github/workflows/publish_to_webserver.yaml` file for details
on configuring the publishing action.
