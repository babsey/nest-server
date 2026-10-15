# helpers.py
#
# This file is part of NEST.
#
# Copyright (C) 2004 The NEST Initiative
#
# NEST is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# NEST is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with NEST.  If not, see <http://www.gnu.org/licenses/>.


# It comments lines starting with 'import' or 'from' otherwise the line number
# of error would be wrong.
def clean_code(source: str) -> str:
    codes = source.split("\n")
    codes_cleaned = []

    for code in codes:
        if code.startswith(("import", "from")):
            codes_cleaned.append("#" + code)
        else:
            codes_cleaned.append(code)

    return "\n".join(codes_cleaned)


def get_arguments(request) -> tuple[list, dict]:
    """Get arguments from the request."""
    args, kwargs = [], {}

    if request.is_json:
        json = request.get_json()

        if isinstance(json, str) and len(json) > 0:
            args = [json]
        elif isinstance(json, list):
            args = json
        elif isinstance(json, dict):
            kwargs = json
            if "args" in kwargs:
                args = kwargs.pop("args")

    elif len(request.form) > 0:
        if "args" in request.form:
            args = request.form.getlist("args")
        else:
            kwargs = request.form.to_dict()

    elif len(request.args) > 0:
        if "args" in request.args:
            args = request.args.getlist("args")
        else:
            kwargs = request.args.to_dict()

    return list(args), kwargs


def str2bool(value: str | None = None) -> bool:
    if value is None:
        return False
    return value.lower() in ("1", "t", "true", "y", "yes")
