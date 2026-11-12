#define _CRT_SECURE_NO_WARNINGS
#include<stdio.h> 
#include<stdlib.h> 
#include<windows.h> 
#include <string.h>
#pragma execution_character_set("utf-8") 

// 调试开关
#define DEBUG 0// 设置为 1 开启调试输出，0 关闭

// 使用克鲁斯卡尔算法求其最小生成树
#define MAX 100 // 最大边/顶点上限（用于静态数组大小）

// 定义边的结构体
typedef struct Edge // 边结构体类型
{
	int start; // 边的起点（顶点编号）
	int end;   // 边的终点（顶点编号）
	int weight; // 边的权重
}Edge; // Edge 为该结构体的别名

// 定义图的结构体
typedef struct Graph // 图结构体类型
{
	int numVertices; // 顶点数量
	int numEdges;    // 当前已添加的边数量
	Edge edges[MAX]; // 存放所有边的数组，最大容量为 MAX
}Graph; // Graph 为该结构体的别名

// 初始化图
void initGraph(Graph* g, int vertices) // 将图的顶点数设为 vertices，并清空边计数
{
	g->numVertices = vertices; // 设置顶点数
	g->numEdges = 0; // 初始无边
}

// 添加一条边
int addEdge(Graph* g, int s, int e, int w) // 向图中加入一条从 s 到 e 的权重为 w 的边
{
	if (g->numEdges >= MAX) return -1; // 超出容量则返回错误
	g->edges[g->numEdges].start = s; // 设置边的起点
	g->edges[g->numEdges].end = e; // 设置边的终点
	g->edges[g->numEdges].weight = w; // 设置边的权重
	g->numEdges++; // 增加边计数
	return 0; // 返回成功
}

//调试
// =======================================================
// 打印排序后的边（用于测试cmpEdge）
void debugPrintSortedEdges(Graph* g)
{
	if (!DEBUG) return;
	printf("\n========== [cmpEdge调试] 排序后的边 ==========\n");
	for (int i = 0; i < g->numEdges; i++)
		printf("  边[%d]: %d -- %d  权重=%d\n", i, g->edges[i].start, g->edges[i].end, g->edges[i].weight);
	printf("==============================================\n\n");
}

// 打印并查集状态（用于测试findSet和unionSet）
void debugPrintUnionFind(int parent[], int rank[], int n, const char* title)
{
	if (!DEBUG) return;
	printf("\n----- [并查集状态] %s -----\n", title);
	printf("  节点:   ");
	for (int i = 1; i <= n; i++) printf("%3d ", i);
	printf("\n  父节点: ");
	for (int i = 1; i <= n; i++) printf("%3d ", parent[i]);
	printf("\n  秩:     ");
	for (int i = 1; i <= n; i++) printf("%3d ", rank[i]);
	printf("\n----------------------------\n");
}

// 打印当前处理的边
void debugPrintEdge(int u, int v, int w, const char* status)
{
	if (!DEBUG) return;
	if (status[0] == '\0')
		printf("\n--- 处理边 %d -- %d (权重=%d) ---\n", u, v, w);
	else if (strcmp(status, "选中") == 0)
		printf("  >> 选中该边（不会成环）\n");
	else if (strcmp(status, "跳过") == 0)
		printf("  XX 跳过该边（会形成环）\n");
}

// 打印根节点信息
void debugPrintRoots(int u, int ru, int v, int rv)
{
	if (!DEBUG) return;
	printf("  [findSet] 节点%d的根=%d, 节点%d的根=%d\n", u, ru, v, rv);
}

// 打印路径压缩信息
void debugPrintCompress(int x, int oldParent, int newParent)
{
	if (!DEBUG) return;
	if (oldParent != newParent)
		printf("  [findSet] 节点%d: 父节点 %d -> %d (路径压缩)\n", x, oldParent, newParent);
}

// 打印合并信息
void debugPrintUnion(int rx, int ry, int rankRx, int rankRy, int result)
{
	if (!DEBUG) return;
	if (rx == ry) {
		printf("  [unionSet] 根相同，跳过\n");
		return;
	}
	if (rankRx < rankRy){
		printf("  [unionSet] %d->%d (低秩挂高秩)\n", rx, ry);
	}
		
	else if (rankRx > rankRy)
		printf("  [unionSet] %d->%d (低秩挂高秩)\n", ry, rx);
	else
		printf(" [unionSet] %d->%d (等秩合并，新秩%d)\n", ry, rx, rankRx + 1);
}
// ===========================================================

// 并查集查找
int findSet(int parent[], int x) // 返回 x 的集合代表（根），并做路径压缩
{
	if (parent[x] != x) {
		int oldParent = parent[x]; // 保存原父节点用于调试
		parent[x] = findSet(parent, parent[x]); // 递归压缩路径
		debugPrintCompress(x, oldParent, parent[x]); // 调试：打印路径压缩
	}
	return parent[x]; // 返回根
}

// 并查集合并
void unionSet(int parent[], int rank[], int x, int y) // 合并 x 和 y 所在集合（按秩合并）
{
	int rx = findSet(parent, x); // 找到 x 的根
	int ry = findSet(parent, y); // 找到 y 的根
	debugPrintUnion(rx, ry, rank[rx], rank[ry], 0); // 调试：打印合并信息
	if (rx == ry) return; // 已在同一集合则不需合并
	if (rank[rx] < rank[ry]) parent[rx] = ry; // 将低秩根挂到高秩根下
	else if (rank[rx] > rank[ry]) parent[ry] = rx; // 反之亦然
	else { parent[ry] = rx; rank[rx]++; } // 若秩相等，任意合并并使新根秩加1
}

// 边按权重升序排序的比较函数
int cmpEdge(const void* a, const void* b) // qsort 使用，按 weight 升序
{
	Edge* ea = (Edge*)a; // 转回 Edge 指针
	Edge* eb = (Edge*)b; // 转回 Edge 指针
	return ea->weight - eb->weight; // 返回差值决定顺序（小到大）
}

// 克鲁斯卡尔算法
void kruskal(Graph* g) // 计算并打印最小生成树的边和总权重
{
	int n = g->numVertices; // 顶点数
	int m = g->numEdges; // 边数
	if (n <= 0) { printf("图顶点数必须大于0\n"); return; }

	// 对边按权重排序
	qsort(g->edges, m, sizeof(Edge), cmpEdge); // 对 edges 数组按权重排序
	debugPrintSortedEdges(g); // 调试：打印排序结果

	int parent[MAX + 1]; // 并查集父节点数组（1-based 索引）
	int rank[MAX + 1]; // 并查集秩数组
	for (int i = 1; i <= n; i++) { parent[i] = i; rank[i] = 0; } // 初始化并查集
	debugPrintUnionFind(parent, rank, n, "初始化后"); // 调试：打印初始状态

	int edgeCount = 0; // 已选边数
	int totalWeight = 0; // 最小生成树总权重
	printf("最小生成树的边:\n"); // 输出表头
	for (int i = 0; i < m && edgeCount < n - 1; i++) // 遍历排序后的边
	{
		int u = g->edges[i].start; // 当前边起点
		int v = g->edges[i].end; // 当前边终点
		int w = g->edges[i].weight; // 当前边权重
		if (u < 1 || u > n || v < 1 || v > n) continue; // 忽略编号不合法的边
		debugPrintEdge(u, v, w, ""); // 调试：打印当前处理的边
		int ru = findSet(parent, u); // 找到 u 的集合根
		int rv = findSet(parent, v); // 找到 v 的集合根
		debugPrintRoots(u, ru, v, rv); // 调试：打印根节点
		if (ru != rv) // 若两端点不在同一集合，则不会成环
		{
			debugPrintEdge(u, v, w, "选中"); // 调试：打印选中状态
			unionSet(parent, rank, ru, rv); // 合并两个集合
			printf("%d -- %d  权重=%d\n", u, v, w); // 输出所选边
			totalWeight += w; // 累加权重
			edgeCount++; // 更新已选边数
			debugPrintUnionFind(parent, rank, n, "合并后"); // 调试：打印合并后状态
		}
		else
		{
			debugPrintEdge(u, v, w, "跳过"); // 调试：打印跳过状态
		}
	}

	if (edgeCount != n - 1) // 若边数不足，则图不连通
	{
		printf("无法构成最小生成树（图可能不连通）。已选边数=%d\n", edgeCount);
	}
	else
	{
		printf("最小生成树总权重 = %d\n", totalWeight); // 输出总权重
	}
}

int main()
{
	Graph g; // 图变量
	int n, m; // n: 顶点数, m: 边数
	// 设置控制台编码为 UTF-8，避免中文输出出现乱码
	SetConsoleOutputCP(CP_UTF8);
	SetConsoleCP(CP_UTF8);
	printf("请输入顶点数（正整数） 和 边数（不超过%d）:\n", MAX); // 提示输入
	char line[256]; // 读入整行输入缓冲
	if (!fgets(line, sizeof(line), stdin) || sscanf(line, "%d %d", &n, &m) != 2) { // 读取 n 和 m
		printf("输入格式错误\n"); // 输入错误处理
		return 1; // 非零表示异常退出
	}
	if (n <= 0 || n > MAX) { printf("顶点数超出范围(1..%d)\n", MAX); return 1; } // 校验 n
	if (m < 0 || m > MAX) { printf("边数超出范围(0..%d)\n", MAX); return 1; } // 校验 m

	initGraph(&g, n); // 初始化图
	printf("请依次输入每条边的 起点 终点 权重（顶点编号从1到 %d）：\n", n); // 提示输入各边
	for (int i = 0; i < m; i++) // 读取 m 条边
	{
		int u, v, w; // 临时变量保存一条边的信息
		if (!fgets(line, sizeof(line), stdin) || sscanf(line, "%d %d %d", &u, &v, &w) != 3)
		{
			printf("边输入格式错误\n"); // 边输入格式错误处理
			return 1;
		}
		if (addEdge(&g, u, v, w) != 0) { printf("无法添加更多边，超出容量\n"); break; } // 添加边并检测容量
	}

	kruskal(&g); // 运行克鲁斯卡尔算法并输出结果
	return 0; // 正常退出
}
