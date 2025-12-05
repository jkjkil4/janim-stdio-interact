# JAnim Stdio Interact

[![MIT License](https://img.shields.io/badge/license-MIT-blue.svg?style=flat)](http://choosealicense.com/licenses/mit/)
[![PyPI Latest Release](https://img.shields.io/pypi/v/janim-stdio-interact.svg?style=flat&logo=pypi)](https://pypi.org/project/janim-stdio-interact/)

<div align="center">

[English](README.md) | **&gt;简体中文&lt;**

</div>

一个用于通过标准输入/输出来与 JAnim GUI 交互并管理窗口的工具库

## 基础用法

通过 stdio 传递 JSON 命令，从而开启与关闭指定的 JAnim GUI.

首先启动 `janim-stdio-i` 程序：

```sh
janim-stdio-i host
```

比如，现在我们需要编译一段代码，构建其中的 Timeline 显示在预览窗口中，向 `stdin` 发送

```json
{"type": "execute", "key": "id1", "source": "from janim.examples import *\nclass A(HelloJAnimExample): pass"}
```

这样就能看到随后打开了一个预览窗口，其中显示的就是经典的 `HelloJAnimExample`.

> [!WARNING]
> 所有发送到 `stdin` 的指令只能占一行，多行指令会被截断

这里 `"key": "id1"` 用于复用窗口，如果你发送相同 `key` 的 `execute` 命令，会把已有窗口中的 Timeline 替换，而不会另外打开一个新的窗口

```json
{"type": "execute", "key": "id1", "source": "from janim.examples import *\nclass A(RotatingPieExample): ..."}
```

传递上面这段命令，就可以看到原来窗口中的 `HelloJAnimExample` 被替换为了 `RotatingPieExample`.

> [!NOTE]
> 如果一段代码中含有多个 Timeline，在初次启动时会使用其中的第一个构建
>
> 在后续重新构建时，替换的时候，会尝试找到和原先同名的 Timeline，如果没有则仍使用其中的第一个构建

如果我们换一个 `key`，比如传递

```json
{"type": "execute", "key": "id2", "source": "from janim.examples import *\nclass A(ArrowPointingExample): ..."}
```

可以发现打开了一个新的窗口来显示，总的来说，就是一个 `key` 对应一个窗口.

另外，除了可以使用 `stdin` 编译以及构建 Timeline，GUI 产生的信息还会通过 `stdout` 返回，具体请参考下面的内容.

## API 参考

### `stdin`

-   `"type": "execute"`

    需提供参数：

    -   `"key"`: 窗口的唯一标识
    -   `"source"`: 以供编译的源代码

    编译并构建 Timeline，在预览窗口中显示

    如果 `key` 所对应的窗口已经存在，则将窗口中原先的 Timeline 替换为新的

    示例：

    ```json
    {"type": "execute", "key": "id1", "source": "from janim.examples import *\nclass A(HelloJAnimExample): pass"}
    ```

-   `"type": "close"`

    需提供参数：

    -   `"key"`: 窗口的唯一标识

    关闭 `key` 所对应的窗口

    示例：

    ```json
    {"type": "close", "key": "id1"}
    ```

### `stdout`

```json
{"type": "viewer-msg", "key": "...", "from": "...", "janim": { ... }}
```

| 字段 | 类型 | 说明 |
| :--- | :--- | :--- |
| `type` | `string` | 固定为 `"viewer-msg"`，标识消息类别 |
| `key` | `string` | 对应创建时的标识符 `key` |
| `from` | `string` | 发送源，可能值：`"execute"`，`"close"`, `"gui"` |
| `janim` | `object` | 具体的事件载荷，包含事件类型及数据 |

当 `"from": "execute"` 时，表示 `stdin` 中 `execute` 命令的执行结果：

-   当源代码中没有可使用的 Timeline 时，载荷是

    ```json
    "janim": {"type": "error", "reason": "no-timeline"}
    ```

-   当 Timeline 构建失败时，载荷是

    ```json
    "janim": {"type": "error", "reason": "build-failed"}
    ```

-   当执行成功时，载荷是

    ```json
    "janim": {"type": "success"}
    ```

当 `"from": "close"` 时，表示 `stdin` 中 `close` 命令的执行结果：

-   当没有对应表示符的预览界面时，载荷是

    ```json
    "janim": {"type": "error", "reason": "not-found"}
    ```

-   当执行成功时，载荷是

    ```json
    "janim": {"type": "success"}
    ```

当 `"from": "gui"` 时，表示 GUI 产生的信息：

-   当界面被创建时，载荷是

    ```json
    "janim": {"type": "created"}
    ```

-   当界面内容被新的替换时，载荷是

    ```json
    "janim": {"type": "rebuilt"}
    ```

-   当预览进度变化时，载荷

    ```json
    "janim": {"type": "lineno", "data": <当前对应的代码行数>}
    ```

-   当界面关闭时，载荷

    ```json
    "janim": {"type": "close_event"}
    ```
