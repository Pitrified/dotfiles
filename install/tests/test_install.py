import logging

import pytest

from install import backup, find_free_dir, is_conf_dir, link_config


@pytest.fixture
def home_dir(tmp_path):
    home = tmp_path / "home"
    home.mkdir()
    return home


@pytest.fixture
def backup_dir(tmp_path):
    backup_dir = tmp_path / ".rcback"
    backup_dir.mkdir()
    return backup_dir


@pytest.fixture
def dotfiles_dir(tmp_path):
    dotfiles_dir = tmp_path / "dotfiles"
    dotfiles_dir.mkdir()
    return dotfiles_dir


# ---------------------------------------------------------------------------
# link_config


def test_link_config_flat_name(home_dir, backup_dir, dotfiles_dir):
    config_at_dot = dotfiles_dir / "bash.symlink"
    config_at_dot.write_text("alias ll='ls -la'\n")

    link_config(config_at_dot, home_dir, backup_dir)

    target = home_dir / ".bash"
    assert target.is_symlink()
    assert target.resolve() == config_at_dot.resolve()


def test_link_config_one_level_nesting(home_dir, backup_dir, dotfiles_dir):
    config_at_dot = dotfiles_dir / "a__b.symlink"
    config_at_dot.write_text("content\n")

    link_config(config_at_dot, home_dir, backup_dir)

    target = home_dir / ".a" / "b"
    assert target.is_symlink()
    assert target.resolve() == config_at_dot.resolve()


def test_link_config_multiple_levels_nesting(home_dir, backup_dir, dotfiles_dir):
    config_at_dot = dotfiles_dir / "a__b__c.symlink"
    config_at_dot.write_text("content\n")

    link_config(config_at_dot, home_dir, backup_dir)

    target = home_dir / ".a" / "b" / "c"
    assert target.is_symlink()
    assert target.resolve() == config_at_dot.resolve()


def test_link_config_directory_source(home_dir, backup_dir, dotfiles_dir):
    config_at_dot = dotfiles_dir / "vim.symlink"
    config_at_dot.mkdir()
    (config_at_dot / "vimrc").write_text("set number\n")

    link_config(config_at_dot, home_dir, backup_dir)

    target = home_dir / ".vim"
    assert target.is_symlink()
    assert target.is_dir()
    assert target.resolve() == config_at_dot.resolve()


def test_link_config_already_linked_is_skipped(home_dir, backup_dir, dotfiles_dir):
    config_at_dot = dotfiles_dir / "bash.symlink"
    config_at_dot.write_text("content\n")
    target = home_dir / ".bash"
    target.symlink_to(config_at_dot)

    link_config(config_at_dot, home_dir, backup_dir)

    assert target.resolve() == config_at_dot.resolve()
    assert list(backup_dir.iterdir()) == []


def test_link_config_warns_on_diverged_real_file(
    caplog, home_dir, backup_dir, dotfiles_dir
):
    config_at_dot = dotfiles_dir / "bash.symlink"
    config_at_dot.write_text("repo content\n")
    target = home_dir / ".bash"
    target.write_text("locally edited content\n")

    with caplog.at_level(logging.WARNING):
        link_config(config_at_dot, home_dir, backup_dir)

    assert any("DIFFERS" in record.message for record in caplog.records)
    assert target.is_symlink()
    assert target.resolve() == config_at_dot.resolve()
    backed_up = backup_dir / ".bash"
    assert backed_up.read_text() == "locally edited content\n"


def test_link_config_no_warning_when_real_file_matches_source(
    caplog, home_dir, backup_dir, dotfiles_dir
):
    config_at_dot = dotfiles_dir / "bash.symlink"
    config_at_dot.write_text("same content\n")
    target = home_dir / ".bash"
    target.write_text("same content\n")

    with caplog.at_level(logging.WARNING):
        link_config(config_at_dot, home_dir, backup_dir)

    assert not any("DIFFERS" in record.message for record in caplog.records)
    # no "matches, leave alone" shortcut: it still gets backed up and relinked
    assert target.is_symlink()
    assert target.resolve() == config_at_dot.resolve()
    assert (backup_dir / ".bash").read_text() == "same content\n"


def test_link_config_dry_run_changes_nothing(home_dir, backup_dir, dotfiles_dir):
    config_at_dot = dotfiles_dir / "a__b.symlink"
    config_at_dot.write_text("content\n")
    target = home_dir / ".a" / "b"

    link_config(config_at_dot, home_dir, backup_dir, dry_run=True)

    assert not target.parent.exists()
    assert not target.exists()
    assert not target.is_symlink()
    assert list(backup_dir.iterdir()) == []


# ---------------------------------------------------------------------------
# backup


def test_backup_moves_existing_file(backup_dir, tmp_path):
    src_at_home = tmp_path / ".bashrc"
    src_at_home.write_text("content\n")

    backup(src_at_home, backup_dir)

    assert not src_at_home.exists()
    assert (backup_dir / ".bashrc").read_text() == "content\n"


def test_backup_moves_existing_dir(backup_dir, tmp_path):
    src_at_home = tmp_path / ".vim"
    src_at_home.mkdir()
    (src_at_home / "vimrc").write_text("content\n")

    backup(src_at_home, backup_dir)

    assert not src_at_home.exists()
    assert (backup_dir / ".vim" / "vimrc").read_text() == "content\n"


def test_backup_moves_dangling_symlink(backup_dir, tmp_path):
    src_at_home = tmp_path / ".bash"
    src_at_home.symlink_to(tmp_path / "nonexistent-target")

    backup(src_at_home, backup_dir)

    assert not src_at_home.is_symlink()
    assert (backup_dir / ".bash").is_symlink()


def test_backup_noop_when_nothing_there(backup_dir, tmp_path):
    src_at_home = tmp_path / ".bashrc"

    backup(src_at_home, backup_dir)

    assert list(backup_dir.iterdir()) == []


def test_backup_dry_run_changes_nothing(backup_dir, tmp_path):
    src_at_home = tmp_path / ".bashrc"
    src_at_home.write_text("content\n")

    backup(src_at_home, backup_dir, dry_run=True)

    assert src_at_home.read_text() == "content\n"
    assert list(backup_dir.iterdir()) == []


# ---------------------------------------------------------------------------
# find_free_dir / is_conf_dir


def test_find_free_dir_picks_unused_suffix(home_dir):
    (home_dir / ".rcback00").mkdir()

    free_dir = find_free_dir(home_dir, ".rcback")

    assert free_dir == home_dir / ".rcback01"


def test_is_conf_dir_true_for_directory(dotfiles_dir):
    topic = dotfiles_dir / "bash"
    topic.mkdir()

    assert is_conf_dir(topic) is True


def test_is_conf_dir_false_for_git(dotfiles_dir):
    git_dir = dotfiles_dir / ".git"
    git_dir.mkdir()

    assert is_conf_dir(git_dir) is False


def test_is_conf_dir_false_for_file(dotfiles_dir):
    not_a_dir = dotfiles_dir / "README.md"
    not_a_dir.write_text("content\n")

    assert is_conf_dir(not_a_dir) is False
