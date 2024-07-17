import asyncio

import aiohttp
import yaml


async def mihomo2quanx(url, path, proxy):
    async with aiohttp.ClientSession() as s:
        async with s.get(url) as resp:
            text = await resp.text()
    rules = yaml.safe_load(text).get("payload", [])
    results = []
    for r in rules:
        if r.startswith("+."):
            results.append(f"host-suffix, {r[2:]}, {proxy}")
        elif "*" in r:
            results.append(f"host-wildcard, {r}, {proxy}")
        elif r.startswith("."):
            results.append(f"host-suffix, {r[1:]}, {proxy}")
        else:
            results.append(f"host, {r}, {proxy}")

    with open(path, "w") as f:
        f.write("\n".join(results))
    print(f"{path} written")


async def main():
    await mihomo2quanx(
        "https://raw.githubusercontent.com/MetaCubeX/meta-rules-dat/meta/geo/geosite/category-cryptocurrency.yaml",
        "quanx_crypto.list",
        "crypto",
    )
    await mihomo2quanx(
        "https://raw.githubusercontent.com/MetaCubeX/meta-rules-dat/meta/geo/geosite/openai.yaml",
        "quanx_openai.list",
        "us",
    )
    await mihomo2quanx(
        "https://raw.githubusercontent.com/MetaCubeX/meta-rules-dat/meta/geo/geosite/anthropic.yaml",
        "quanx_anthropic.list",
        "us",
    )


if __name__ == "__main__":
    asyncio.run(main())
