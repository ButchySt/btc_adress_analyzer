# Bitcoin Address Analyzer / 比特币地址分析器

[English](#english) | [中文](#chinese)

<a name="english"></a>
## English

A Python tool to analyze and visualize Bitcoin address transaction relationships.

### Features

- **Multi-Address Analysis**: Accepts multiple Bitcoin addresses as input.
- **Recursive Tracing**: Traces upstream (senders) and downstream (receivers) up to a specified depth (level).
- **Time-Aware Filtering**:
    - Supports specifying a start and end date for the initial addresses.
    - For deeper levels, automatically filters transactions to a **1-week window** around the relevant transaction time, significantly reducing noise and processing time.
- **Relevance Filtering**: Automatically filters the final graph to show only nodes and edges that form paths between the initial addresses, removing unrelated clutter.
- **Visualization**: Generates a clear network graph highlighting the initial addresses (red) and their connections.
- **Data Export**: Option to save full and filtered graph data and raw transactions to JSON.
- **Progress Tracking**: Shows progress bars for data fetching.

### Installation

1.  Clone the repository.
2.  Create a virtual environment (optional but recommended):
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate  # On Windows use: .venv\Scripts\activate
    ```
3.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

### Usage

Run the tool from the command line:

```bash
python main.py <address1> [address2 ...] [options]
```

#### Arguments

- `addresses`: One or more Bitcoin addresses to analyze.
- `--level`: Depth of analysis (default: 1).
    - Level 1: Direct neighbors.
    - Level 2: Neighbors of neighbors.
- `--output`: Output image filename (default: `graph.png`).
- `--save-data`: Save full graph, filtered graph, and raw transaction data to JSON files.
- `--start-date`: Start date for the initial addresses (format: YYYY-MM-DD).
- `--end-date`: End date for the initial addresses (format: YYYY-MM-DD).

#### Examples

**Basic Analysis (Level 1):**
```bash
python main.py 1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa --level 1 --output genesis.png
```

**Deep Analysis with Time Filter and Data Saving:**
Analyze relationships between multiple addresses at Level 2, focusing on transactions in 2020, and save the data:
```bash
python main.py 1AddressA 1AddressB --level 2 --start-date 2020-01-01 --end-date 2020-12-31 --save-data --output result.png
```

### Notes

- This tool uses the Blockchain.info API.
- The tool uses batch processing to respect API limits and improve speed.
- "Relevance Filtering" ensures that the final visualization focuses on how the input addresses are connected to each other.

---

<a name="chinese"></a>
## 中文 (Chinese)

一个用于分析和可视化比特币地址交易关系的 Python 工具。

### 功能特点

- **多地址分析**：支持同时输入多个比特币地址进行分析。
- **递归追踪**：支持指定深度（层级），递归追踪上游（发送方）和下游（接收方）。
- **时间感知过滤**：
    - 支持为初始地址指定开始和结束日期。
    - 对于更深层级的地址，自动过滤出相关交易发生时间前后 **1周** 内的交易，显著减少噪音和处理时间。
- **相关性筛选**：自动过滤最终的图表，仅显示构成初始地址之间路径的节点和边，去除无关的干扰数据。
- **可视化**：生成清晰的网络图，高亮显示初始地址（红色）及其连接关系。
- **数据导出**：支持将完整图数据、筛选后的图数据以及原始交易数据保存为 JSON 文件。
- **进度追踪**：显示数据获取的进度条。

### 安装步骤

1.  克隆仓库。
2.  创建虚拟环境（可选但推荐）：
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate  # Windows 用户使用: .venv\Scripts\activate
    ```
3.  安装依赖：
    ```bash
    pip install -r requirements.txt
    ```

### 使用方法

在命令行中运行工具：

```bash
python main.py <地址1> [地址2 ...] [选项]
```

#### 参数说明

- `addresses`: 一个或多个要分析的比特币地址。
- `--level`: 分析深度（默认为 1）。
    - Level 1: 直接交易对手。
    - Level 2: 交易对手的对手。
- `--output`: 输出图片文件名（默认为 `graph.png`）。
- `--save-data`: 保存完整图、筛选后的图和原始交易数据到 JSON 文件。
- `--start-date`: 初始地址的开始日期（格式：YYYY-MM-DD）。
- `--end-date`: 初始地址的结束日期（格式：YYYY-MM-DD）。

#### 示例

**基础分析（Level 1）：**
```bash
python main.py 1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa --level 1 --output genesis.png
```

**带时间过滤和数据保存的深度分析：**
分析多个地址在 Level 2 的关系，仅关注 2020 年的交易，并保存数据：
```bash
python main.py 1AddressA 1AddressB --level 2 --start-date 2020-01-01 --end-date 2020-12-31 --save-data --output result.png
```

### 注意事项

- 本工具使用 Blockchain.info API。
- 工具使用批量处理以遵守 API 限制并提高速度。
- “相关性筛选”确保最终的可视化结果专注于输入地址之间的连接关系。

