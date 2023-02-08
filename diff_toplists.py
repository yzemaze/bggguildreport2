import argparse
import datetime
import gettext
import json
import logging


def print_list(old_file, new_file, style):

    with open(old_file, "r") as oldf:
        old_lists = json.load(oldf)

    with open(new_file, "r") as newf:
        new_lists = json.load(newf)

    new_top = new_lists["lists"][0]["games"]
    old_top = old_lists["lists"][0]["games"]
    old_top_gameids = [x[1] for x in old_top]
    old_top_means = [x[3] for x in old_top]
    old_top_ratings = [x[2] for x in old_top]

    hlevel = "h3"
    headline = _("Top Diff")
    ths = [
        _("No."),
        _("+/-"),
        _("Game"),
        _("Ratings"),
        _("+/-"),
        _("Mean"),
        _("+/-"),
        _("SD")]

    # table header
    if style == "html":
        print(f"<style>\n"
              f".text-right {{text-align: right; padding: 0 5px;}}\n"
              f"</style>", file=of)
        print(f"<{hlevel}>{headline}</{hlevel}>", file=of)
        print(f"<table id={headline.replace(' ', '_')}>\n<thead>\n<tr>", file=of)
        for i, th in enumerate(ths):
            print(f"<th>{th}</th>", file=of)
        print(f"</tr>\n</thead>\n<tbody>", file=of)
    elif style == "bbcode":
        print(f"[{hlevel}]{headline}[/{hlevel}]", file=of)
        print("[table]\n[tr]", file=of)
        for i, th in enumerate(ths):
            print(f"[th]{th}[/th]", file=of)
        print("[/tr]", file=of)
    else:
        name_width = max([len(x[0]) for x in new_top])
        ratings_width = max(len(ths[3]), 4)
        mean_width = max(len(ths[5]), 5)
        print("[b]Top[/b]\n[c]", file=of)
        print(f"{ths[0]:3} {ths[1]:5} {ths[2]:{name_width}} "
              f"{ths[3]:{ratings_width}} {ths[4]:6} "
              f"{ths[5]:{mean_width}} {ths[6]:9} {ths[7]:5}",
              file=of)

    # table content
    for index, game_info in enumerate(new_top):
        try:
            old_index = old_top_gameids.index(game_info[1])
        except ValueError:
            old_index = -1

        if old_index > -1:
            diff_index = f"{old_index - index:>+3}"
            diff_ratings = f"{game_info[2] - old_top_ratings[old_index]:>+3}"
            diff_mean = f"{game_info[3] - old_top_means[old_index]:+.3f}"
        else:
            diff_index = _("new")
            diff_ratings = ""
            diff_mean = ""
        if style == "html":
            print(f"<tr>\n"
                  f"<td class=\"text-right\">{index + 1}</td>\n"
                  f"<td class=\"text-right\">{diff_index}</td>\n"
                  f"<td>{game_info[0]}</td>\n"
                  f"<td class=\"text-right\">{game_info[2]}</td>\n"
                  f"<td class=\"text-right\">{diff_ratings}</td>\n"
                  f"<td class=\"text-right\">{game_info[3]:.3f}</td>\n"
                  f"<td class=\"text-right\">{diff_mean}</td>\n"
                  f"<td class=\"text-right\">{game_info[4]:.3f}</td>\n"
                  f"</tr>",
                  file=of)
        elif style == "bbcode":
            print(f"[tr]\n"
                  f"[td]{index + 1}[/td]\n"
                  f"[td]{diff_index}[/td]\n"
                  f"[td]{game_info[0]}[/td]\n"
                  f"[td]{game_info[2]}[/td]\n"
                  f"[td]{diff_ratings}[/td]\n"
                  f"[td]{game_info[3]:.3f}[/td]\n"
                  f"[td]{diff_mean}[/td]\n"
                  f"[td]{game_info[4]:.3f}[/td]\n"
                  f"[/tr]",
                  file=of)
        else:
            print(f"{index+1:3} {diff_index:5} "
                  f"{game_info[0]:{name_width}} "
                  f"{game_info[2]:{ratings_width}} {diff_ratings:6} "
                  f"{game_info[3]:{mean_width}.3f} {diff_mean:8} "
                  f"{game_info[4]:6.3f}", file=of)

    # table footer
    if style == "html":
        print("</tbody>\n</table>", file=of)
    elif style == "bbcode":
        print("[/table]", file=of)
    else:
        print("[/c]", file=of)

if __name__ == "__main__":
    logging.basicConfig(filename="std.log", encoding="utf-8",
                        format="%(asctime)s %(message)s", level=logging.DEBUG)
    logger = logging.getLogger()

    parser = argparse.ArgumentParser(
        description="Print top x with diffs in a pretty format")
    parser.add_argument(
        "old",
        help="old top file")
    parser.add_argument(
        "new",
        help="new top file")
    parser.add_argument(
        "--style",
        default="html",
        help="output format: bbcode|bgg|html - default: html")
    parser.add_argument(
        "--lang",
        default="en",
        help="language for headlines and tableheaders - default: en")
    args = parser.parse_args()

    lang = gettext.translation("diff_toplists", localedir="locales",
                               languages=[args.lang])
    lang.install()
    _ = lang.gettext

    if (args.style == "bgg") or (args.style == "bbcode"):
        style = args.style
        ext = "txt"
    else:
        style = "html"
        ext = "html"

    date_str = datetime.datetime.now().strftime("%Y%m%d")
    filename = f"topdiff_{date_str}.{ext}"
    with open(filename, "w") as of:
        print_list(args.old, args.new, style)

    logger.info(f"+/- saved to {filename}")