# %%
import os
import asyncio
import aiohttp
import ipaddress

import nest_asyncio

nest_asyncio.apply()


async def get_content(urls):
    if isinstance(urls, str):
        urls = [urls]
    contents = []
    async with aiohttp.ClientSession() as s:
        for url in urls:
            if not url.startswith("http://"):
                url = os.path.join(
                    "https://raw.githubusercontent.com/",
                    "MetaCubeX/meta-rules-dat/refs/heads/meta",
                    url,
                )
            async with s.get(url) as resp:
                text = await resp.text()
                contents.append(text.strip())
    return "\n".join(contents)


async def download_save(urls, name, raw=None):
    content = await get_content(urls)
    if isinstance(raw, list):
        content = content.strip() + "\n" +\
            "\n".join([r.strip() for r in raw])
    elif isinstance(raw, str):
        content = content.strip() + "\n" +\
            raw.strip()
    write_list(content, name)


def write_list(l, name):
    file = f"output/{name}.list"
    with open(file, "w") as f:
        content = "\n".join(l) if isinstance(l, list) else l
        f.write(content)
    print(f"{file} written")


# %%
def simplify_gfw(content):
    white = {"+.com", "+.org", ".net", "+.hk"}
    result = set()
    for line in content.splitlines():
        if line.startswith("+.") or line.startswith("*."):
            line = line[2:]
        elif line.startswith("."):
            line = line[1:]

        domains = line.split(".")
        if len(domains) < 1:
            continue

        for i in range(len(domains)):
            target = "+." + ".".join(domains[-(i + 1) :])
            # print(f"{line}\ttest: {i} {target}")
            if i == 0 and target not in white:
                result.add(target)
                break
            if target in result:
                break
            if i == 1 and target not in result:
                result.add(target)
                break
    results = []
    for r in result:
        if not r.strip() or not r.strip("+."):
            continue
        if r.endswith(".cn"):
            continue
        results.append(r)
    results.sort()
    return results


# %%
def merge_cidrs(cidr_list):
    ipv4_networks, ipv6_networks = [], []
    for cidr in cidr_list:
        if cidr.startswith("0."):
            continue
        try:
            network = ipaddress.ip_network(cidr, strict=False)
            if isinstance(network, ipaddress.IPv4Network):
                ipv4_networks.append(network)
            else:
                ipv6_networks.append(network)
        except ValueError as e:
            print(f"无效的CIDR地址: {cidr} - {e}")
            continue
    merged_v4 = list(ipaddress.collapse_addresses(ipv4_networks))
    merged_v6 = list(ipaddress.collapse_addresses(ipv6_networks))
    all_merged = merged_v4 + merged_v6
    # return [str(net) for net in all_merged]
    return [str(net) for net in merged_v4]


async def main():
    print("Hello from rules!")

    sitegfw = await get_content(
        [
            "geo/geosite/gfw.list",
            "geo/geosite/zoom.list",
            "geo/geosite/slack.list",
        ]
    )
    sitegfw = simplify_gfw(sitegfw)
    write_list(sitegfw, "sitegfw")

    await download_save(
        [
            "geo/geosite/private.list",
            "geo-lite/geosite/cn.list",
        ],
        "sitecn",
        [
            # for apple
            "+.icloud.com",
            "+.itunes.com",
            "+.apple.com",
            "+.applemusic.com",
            "+.omtrdc.net",
            "+.cdn-apple.com",
            "+.apple-dns.net",
            "+.akadns.net",
            "+.icloud-content.com",
            "+.apple-studies.com",
        ]
    )

    await download_save(
        "geo/geosite/category-cryptocurrency.list",
        "sitecrypto",
    )

    await download_save(
        "geo/geosite/category-ai-!cn.list",
        "siteai",
    )

    ips = await get_content(
        [
            "geo/geoip/cn.list",
            "geo/geoip/private.list",
            "geo-lite/geoip/cn.list",
        ]
    )
    merged = merge_cidrs(ips.strip().splitlines())
    write_list(merged, "ipcnprivate")

    iptg = await get_content("geo/geoip/telegram.list")
    merged = merge_cidrs(iptg.strip().splitlines())
    write_list(merged, "iptg")


if __name__ == "__main__":
    asyncio.run(main())
