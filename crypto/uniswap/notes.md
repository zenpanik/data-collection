
# How to filter by pool id
```

where : {}
      pool_contains: "0x8ad599c3a0ff1de082011efddc58f1908eb6e6d8"
    }
```

```
{
  ticks (first:100
    where : {
      pool_contains: "0x8ad599c3a0ff1de082011efddc58f1908eb6e6d8"
    }){
    id
    tickIdx
    price0
    price1
    volumeToken0
    volumeToken1
    collectedFeesToken0
    collectedFeesToken1
    liquidityProviderCount
    createdAtTimestamp
  }
}
```

```
"query surroundingTicks($poolAddress: String!, $tickIdxLowerBound: BigInt!, $tickIdxUpperBound: BigInt!, $skip: Int!) {\n ticks(\n subgraphError: allow\n first: 1000\n skip: $skip\n where: {poolAddress: $poolAddress, tickIdx_lte: $tickIdxUpperBound, tickIdx_gte: $tickIdxLowerBound}\n ) {\n tickIdx\n liquidityGross\n liquidityNet\n price0\n price1\n __typename\n }\n}\n"

tickIdxLowerBound	184500
tickIdxUpperBound	208500
poolAddress	"0x8ad599c3a0ff1de082011efddc58f1908eb6e6d8"
skip	0

```