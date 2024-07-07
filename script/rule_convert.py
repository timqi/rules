import asyncio

import aiohttp
import yaml


async def mihomo2quanx(url, path):
    async with aiohttp.ClientSession() as s:
        async with s.get(url) as resp:
            text = await resp.text()
    rules = yaml.safe_load(text).get("payload", [])
    results = []
    for r in rules:
        if r.startswith("+."):
            results.append(f"host-suffix, {r[2:]}, crypto")
        elif "*" in r:
            results.append(f"host-wildcard, {r}, crypto")
        elif r.startswith("."):
            results.append(f"host-suffix, {r[1:]}, crypto")
        else:
            results.append(f"host, {r}, crypto")

    with open(path, "w") as f:
        f.write("\n".join(results))
    print(f"{path} written")


async def main():
    await mihomo2quanx(
        "https://raw.githubusercontent.com/MetaCubeX/meta-rules-dat/meta/geo/geosite/category-cryptocurrency.yaml",
        "quanx_crypto.list",
    )
    await mihomo2quanx(
        "https://raw.githubusercontent.com/MetaCubeX/meta-rules-dat/meta/geo/geosite/openai.yaml", "quanx_openai.list"
    )


if __name__ == "__main__":
    asyncio.run(main())
