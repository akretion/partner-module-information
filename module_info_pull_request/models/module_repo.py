import logging
from datetime import datetime

import requests

from odoo import fields, models

# from odoo.tools import date_utils

_logger = logging.getLogger(__name__)


class ModuleRepo(models.Model):
    _inherit = "module.repo"

    date_last_updated = fields.Datetime(string="Last Update date", readonly=True)
    ignore_pr_import = fields.Boolean()

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

    def import_pr(self):
        git_token = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("module.info.pull.request.git.token")
        )
        odoo_version_dct = {v.name: v.id for v in self.env["odoo.version"].search([])}
        for repo in self:
            modules = {m.name: m.id for m in repo.module_ids}
            if repo.date_last_updated:
                # call api search, sort by date desc
                # stop pagination when date correspond to date_last_updated
                page = 1
                prs = []
                while True:
                    url = (
                        f"https://api.github.com/repos/{repo.organization}"
                        f"/{repo.name}/pulls?state=all&per_page=10&page={page}"
                        "&sort=updated&direction=desc"
                    )
                    response = requests.get(
                        url,
                        headers={"authorization": f"Bearer {git_token}"},
                        timeout=120,
                    )
                    if len(response.json()):
                        prs.extend(response.json())
                        if (
                            datetime.strptime(
                                response.json()[-1]["updated_at"], "%Y-%m-%dT%H:%M:%SZ"
                            )
                            < repo.date_last_updated
                        ):
                            break
                    page += 1
            else:
                # Init of PR's repo
                # Call api pulls to get all openned pr
                page = 1
                result = 1
                prs = []
                while result:
                    url = (
                        f"https://api.github.com/repos/{repo.organization}"
                        f"/{repo.name}/pulls?per_page=40&page={page}"
                    )
                    response = requests.get(
                        url,
                        headers={"authorization": f"Bearer {git_token}"},
                        timeout=120,
                    )
                    if len(response.json()):
                        prs.extend(response.json())
                    result = len(response.json())
                    page += 1

            if prs:
                max_updated = prs[0]["updated_at"]
            for pr in prs:
                if not odoo_version_dct.get(pr["base"]["ref"][:4], False):
                    continue
                self.env["pull.request"].create_or_update_pr(
                    pr, repo, modules, odoo_version_dct
                )
                max_updated = max(pr["updated_at"], max_updated)
            if prs:
                repo.date_last_updated = datetime.strptime(
                    max_updated, "%Y-%m-%dT%H:%M:%SZ"
                ).strftime("%Y-%m-%d")

    def get_pr_state(self):
        self.import_pr()
        return True
