import yaml
import aiohttp
import asyncio


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


if __name__ == "__main__":
    crypto_url = (
        "https://raw.githubusercontent.com/MetaCubeX/meta-rules-dat/meta/geo/geosite/category-cryptocurrency.yaml"
    )
    asyncio.run(mihomo2quanx(crypto_url, "quanx_crypto.list"))
