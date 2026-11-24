`prices[i]` is the price of a stock on day `i`. Choose **one** day to buy and a **later** day to sell, and return the largest profit you can make. If no trade makes money, return `0`.

### Examples

- `prices = [7, 1, 5, 3, 6, 4]` → `5` (buy at 1 on day 1, sell at 6 on day 4)
- `prices = [7, 6, 4, 3, 1]` → `0` (prices only fall, so do not trade)

### Constraints

- `1 <= len(prices) <= 10^5`
- `0 <= prices[i] <= 10^4`

**Challenge:** checking every buy/sell pair is $O(n^2)$. Can you do it in one pass?
