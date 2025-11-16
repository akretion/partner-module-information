import logging

from github import Auth, Github

from odoo import api, fields, models

from ..tools import naive_dt

# from odoo.tools import date_utils

_logger = logging.getLogger(__name__)


class ModuleRepo(models.Model):
    _inherit = "module.repo"

    date_last_updated = fields.Datetime(string="Last Update date")
    ignore_pr_import = fields.Boolean(
        compute="_compute_ignore_pr_import",
        store=True,
        readonly=False,
    )

    @api.depends("url")
    def _compute_ignore_pr_import(self):
        for record in self:
            record.ignore_pr_import = not record.url or not record.url.startswith(
                "https://github.com"
            )

    def cron_import_pr(self):
        repos = self.search([("ignore_pr_import", "!=", True)])
        # delay job in time because github have some request limit by hours
        # let's say we want it to be processed in more or less 12H
        job_num_by_hour = int(len(repos) / 12)
        eta = 0
        for i, repo in enumerate(repos, 1):
            repo.with_delay(
                max_retries=2,
                eta=eta,
                description="import PR infos for repo: "
                f"{repo.organization}/{repo.name}",
            ).import_pr()
            if i % job_num_by_hour == 0:
                eta += 60 * 60

    def _get_github_client(self):
        github_token = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("module.info.pull.request.git.token")
        )
        if github_token:
            g = Github(auth=Auth.Token(github_token))
        else:
            g = Github()
        return g

    def import_pr(self):
        g = self._get_github_client()
        for repo in self:
            gh_repo = g.get_repo(f"{repo.organization}/{repo.name}")
            state = "all" if repo.date_last_updated else "open"
            last_updated = repo.date_last_updated
            new_last_updated = None
            for pr in gh_repo.get_pulls(state=state, sort="updated", direction="desc"):
                if last_updated and last_updated >= naive_dt(pr.updated_at):
                    # stop as this PR have been already processed
                    break
                if not new_last_updated:
                    new_last_update = naive_dt(pr.updated_at)
                self._create_or_update_pr(pr)
            if new_last_updated:
                repo.date_last_updated = new_last_update

    def import_pr_number(self, number):
        self.ensure_one()
        g = self._get_github_client()
        gh_repo = g.get_repo(f"{self.organization}/{self.name}")
        gh_pr = gh_repo.get_pull(number)
        return self._create_or_update_pr(gh_pr)

    def _create_or_update_pr(self, gh_pr):
        self.ensure_one()
        pr_obj = self.env["pull.request"]
        pr = pr_obj.search([("number", "=", gh_pr.number), ("repo_id", "=", self.id)])
        if pr:
            vals = pr._prepare_update_pr(self, gh_pr)
            pr.write(vals)
        else:
            vals = pr_obj._prepare_create_pr(self, gh_pr)
            pr = pr_obj.create(vals)
        pr._update_module_version()
        return pr

    def get_pr_state(self):
        self.import_pr()
        return True
