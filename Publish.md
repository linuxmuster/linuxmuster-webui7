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
