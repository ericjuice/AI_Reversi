import math
import random
import sys

from game import Game   # 导入黑白棋文件
from copy import deepcopy


class RandomPlayer:
    """
    随机玩家, 随机返回一个合法落子位置
    """

    def __init__(self, color):
        """
        玩家初始化
        :param color: 下棋方，'X' - 黑棋，'O' - 白棋
        """
        self.color = color

    def random_choice(self, board):
        """
        从合法落子位置中随机选一个落子位置
        :param board: 棋盘
        :return: 随机合法落子位置, e.g. 'A1' 
        """
        # 用 list() 方法获取所有合法落子位置坐标列表
        action_list = list(board.get_legal_actions(self.color))

        # 如果 action_list 为空，则返回 None,否则从中选取一个随机元素，即合法落子坐标
        if len(action_list) == 0:
            return None
        else:
            return random.choice(action_list)

    def get_move(self, board):
        """
        根据当前棋盘状态获取最佳落子位置
        :param board: 棋盘
        :return: action 最佳落子位置, e.g. 'A1'
        """
        if self.color == 'X':
            player_name = '黑棋'
        else:
            player_name = '白棋'
        print("请等一会，对方 {}-{} 正在思考中...".format(player_name, self.color))
        action = self.random_choice(board)
        return action


class HumanPlayer:
    """
    人类玩家
    """

    def __init__(self, color):
        """
        玩家初始化
        :param color: 下棋方，'X' - 黑棋，'O' - 白棋
        """
        self.color = color

    def get_move(self, board):
        """
        根据当前棋盘输入人类合法落子位置
        :param board: 棋盘
        :return: 人类下棋落子位置
        """
        # 如果 self.color 是黑棋 "X",则 player 是 "黑棋"，否则是 "白棋"
        if self.color == "X":
            player = "黑棋"
        else:
            player = "白棋"

        # 人类玩家输入落子位置，如果输入 'Q', 则返回 'Q'并结束比赛。
        # 如果人类玩家输入棋盘位置，e.g. 'A1'，
        # 首先判断输入是否正确，然后再判断是否符合黑白棋规则的落子位置
        while True:

            action = input(
                "请'{}-{}'方输入一个合法的坐标(e.g. 'D3'，若不想进行，请务必输入'Q'结束游戏。): ".format(player,
                                                                             self.color))

            # 如果人类玩家输入 Q 则表示想结束比赛
            if action == "Q" or action == 'q':
                return "Q"
            else:
                row, col = action[1].upper(), action[0].upper()

                # 检查人类输入是否正确
                if row in '12345678' and col in 'ABCDEFGH':
                    # 检查人类输入是否为符合规则的可落子位置
                    if action in board.get_legal_actions(self.color):
                        return action
                else:
                    print("你的输入不合法，请重新输入!")


class Node:
    def __init__(self, now_board, parent=None, action=None, color=""):
        self.visits = 0  # 访问次数
        self.reward = 0.0  # 期望值
        self.now_board = now_board  # 棋盘状态
        self.children = []  # 孩子节点
        self.parent = parent  # 父节点
        self.action = action  # 对应动作
        self.color = color  # 该节点玩家颜色

    def get_ucb(self, ucb_param):
        if self.visits == 0:
            return sys.maxsize  # 未访问的节点ucb为无穷大

        # UCB公式
        explore = math.sqrt(2.0 * math.log(self.parent.visits) / float(self.visits))
        now_ucb = self.reward/self.visits + ucb_param * explore
        return now_ucb

    # 生个孩子
    def add_child(self, child_now_board, action, color):
        child_node = Node(child_now_board, parent=self, action=action, color=color)
        self.children.append(child_node)

    # 判断是否完全扩展
    def full_expanded(self):
        # 有孩子并且所有孩子都访问过了就是完全扩展
        if len(self.children) == 0:
            return False
        for kid in self.children:
            if kid.visits == 0:
                return False
        # if len(self.children) == len(list(self.now_board.get_legal_actions(self.color))):
        #    return True
        return True


class AIPlayer:
    """
    AI 玩家
    """

    def __init__(self, color):
        """
        玩家初始化
        :param color: 下棋方，'X' - 黑棋，'O' - 白棋
        """
        self.max_times = 50  # 最大迭代次数
        self.ucb_param = 1.5  # ucb的参数C

        self.color = color

    def uct(self, max_times, root):
        """
        根据当前棋盘状态获取最佳落子位置
        :param max_times: 最大搜索次数
        :param root: 根节点
        :return: action 最佳落子位置
        """

        for i in range(max_times):  # 最多模拟max次
            selected_node = self.select(root)
            leaf_node = self.extend(selected_node)
            reward = self.stimulate(leaf_node)
            self.backup(leaf_node, reward)

        max_node= None     # 搜索完成，然后找出最适合的下一步
        max_ucb = -sys.maxsize
        for child in root.children:
            child_ucb = child.get_ucb(self.ucb_param)
            if max_ucb < child_ucb:
                max_ucb = child_ucb
                max_node = child  # max_node指向ucb最大的孩子

        return max_node.action

    def select(self, node):
        """
        :param node:某个节点
        :return: ucb值最大的叶子
        """
        # print(len(node.children))
        if len(node.children) == 0:   # 叶子，需要扩展
            return node
        if node.full_expanded():    # 完全扩展,递归选择ucb最大的孩子
            max_node = None
            max_ucb = -sys.maxsize
            for child in node.children:
                child_ucb = child.get_ucb(self.ucb_param)
                if max_ucb < child_ucb:
                    max_ucb = child_ucb
                    max_node = child    # max_node指向ucb最大的孩子
            return self.select(max_node)

        else:   # 没有完全扩展就选访问次数为0的孩子
            for kid in node.children:   # 从左开始遍历
                if kid.visits == 0:
                    return kid

    def extend(self, node):
        if node.visits == 0:    # 自身还没有被访问过，不扩展，直接模拟
            return node
        else:   # 需要扩展,先确定颜色
            if node.color == 'X':
                new_color = 'O'
            else:
                new_color = 'X'
            for action in list(node.now_board.get_legal_actions(node.color)):  # 把所有可行节点加入孩子列表，并初始化
                new_board = deepcopy(node.now_board)
                new_board._move(action, node.color)
                # 新建节点
                node.add_child(new_board, action=action, color=new_color)
            if len(node.children) == 0:
                return node
            return node.children[0]     # 返回新的孩子列表的第一个，以供下一步模拟

    def stimulate(self, node):
        """
        :param node:模拟起始点
        :return: 模拟结果reward
        board.get_winner()会返回胜负关系和获胜子数
        考虑胜负关系和获胜的子数，定义获胜积10分，每多赢一个棋子多1分
        """

        board = deepcopy(node.now_board)
        color = node.color
        count = 0
        while (not self.game_over(board)) and count < 50:   # 游戏没有结束，就模拟下棋
            action_list = list(node.now_board.get_legal_actions(color))
            if not len(action_list) == 0:   # 可以下，就随机下棋
                action = random.choice(action_list)
                board._move(action, color)
                if color == 'X':
                    color = 'O'
                else:
                    color = 'X'
            else:   # 不能下，就交换选手
                if color == 'X':
                    color = 'O'
                else:
                    color = 'X'
                action_list = list(node.now_board.get_legal_actions(color))
                action = random.choice(action_list)
                board._move(action, color)
                if color == 'X':
                    color = 'O'
                else:
                    color = 'X'
            count = count + 1

        # winner:0-黑棋赢，1-白旗赢，2-表示平局
        # diff:赢家领先棋子数
        winner, diff = board.get_winner()
        if winner == 2:
            reward = 0
        elif winner == 0:   # 这里是反的。。出bug了负负得正
            reward = 10 + diff
        else:
            reward = -(10 + diff)

        if self.color == 'X':
            reward = -reward

        return reward

    def backup(self, node, reward):
        """
        反向传播函数
        """
        while node is not None:
            node.visits += 1
            if node.color == self.color:
                node.reward += reward
            else:
                node.reward -= reward
            node = node.parent
        return 0

    def game_over(self, board):
        """
        判断游戏是否结束
        :return: True/False 游戏结束/游戏没有结束
        """
        # 根据当前棋盘，双方都无处可落子，则终止
        b_list = list(board.get_legal_actions('X'))
        w_list = list(board.get_legal_actions('O'))
        is_over = (len(b_list) == 0 and len(w_list) == 0)  # 返回值 True/False

        return is_over

    def get_move(self, board):
        """
        根据当前棋盘状态获取最佳落子位置
        :param board: 棋盘
        :return: action 最佳落子位置, e.g. 'A1'
        """
        if self.color == 'X':
            player_name = '黑棋'
        else:
            player_name = '白棋'
        print("请等一会，对方 {}-{} 正在思考中...".format(player_name, self.color))

        # -----------------请实现你的算法代码--------------------------------------
        root = Node(now_board=deepcopy(board), color=self.color)

        action = self.uct(self.max_times, root)
        # ------------------------------------------------------------------------

        return action


# 黑棋初始化
black_player = AIPlayer("X")

# 白棋初始化
white_player = RandomPlayer("O")

# 游戏初始化，第一个玩家是黑棋，第二个玩家是白棋
game = Game(black_player, white_player)
# 开始下棋
game.run()
