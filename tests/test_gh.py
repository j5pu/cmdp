from nodeps.fixtures import Repos, repos


def test_fixture_repos(repos: Repos):
    """Test that repos are created and pushed."""
    assert (repos.local.top / "README.md").is_file()
    assert repos.local.git.cat_file("-e", "origin/main:README.md") == ""

