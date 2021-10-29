# Creating a release
### The following steps have to be followed to create a release:
1. Update the changelog file
2. Update the version code in the .pro file
3. commit all changes
4. Do a git push: `git push`
6. Create a git tag in the format v+VERSION (eg. v7.0.0): `git tag vVERSION`
7. Push tags: `git push --tags`

### In case of a mistake, the tag can be deleted:
1. Locally: `git tag -d vVERSION`
2. Remotely: `git push --delete origin vVERSION`

# Version schema:
- Genreal: `major.minor.patch`
- Prereleases (release candidates) must end with `-rcXX` where `XX` is the number of the Prerelease
  - So, before version `7.1.1` is released, there may be versions `7.1.1-rc01`, `7.1.1-rc02`, and so on
- Releases are always prefixed with `release`.
  - So, once version `7.1.1` is ready, it is published as `7.1.1-release`
- This concept ensures that stable releases are elays evaluated as a higher version Number than perreleases.
