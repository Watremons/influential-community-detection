import time

from utils.argparser import args_parser
from utils.ioutils import data_graph_read, mid_graph_save, index_save, mid_graph_read, index_read, is_precomputed, is_indexed, result_graph_save, statistic_file_save
from online.statistics import Statistics
from precompute import execute_offline, construct_index
from process import execute_online


def count_leaf_node(now_index):
    if len(now_index) == 0:
        return 0
    if now_index[0]["T"]:
        return 1
    now_counter = 0
    for next_index_entry in now_index:
        now_counter += count_leaf_node(next_index_entry["P"])
    return now_counter


if __name__ == "__main__":
    args = args_parser()
    stat = Statistics(
        input_file_folder=args.input,
        query_keyword_Q=[int(keyword) for keyword in args.keywords.split(",")],
        query_support_k=args.support,
        radius_r=args.radius,
        threshold_theta=args.theta,
        query_L=args.top,
    )
    if not is_precomputed(args.input):
        print("No available precomputed graph!")
        print("Start offline pre-computation:")
        data_graph = data_graph_read(args.input)
        mid_data_graph = execute_offline(data_graph=data_graph)
        mid_graph_save(mid_data_graph=data_graph, dataset_path=args.input)
    if not is_indexed(args.input):
        print("No available index!")
        print("Start index construction:")
        mid_data_graph = mid_graph_read(dataset_path=args.input)
        index_root = construct_index(data_graph=mid_data_graph)
        index_save(index=index_root, dataset_path=args.input)
    print("Load precomputed data graph:")
    mid_data_graph = mid_graph_read(dataset_path=args.input)
    print("Load constructed index:")
    index_root = index_read(dataset_path=args.input)
    print("Start online processing:")
    stat.start_timestamp = time.time()
    result_set = execute_online(
        data_graph=mid_data_graph,
        query_keyword_Q=[int(keyword) for keyword in args.keywords.split(",")],
        query_support_k=args.support,
        radius_r=args.radius,
        threshold_theta=args.theta,
        query_L=args.top,
        index_root=index_root,
        stat=stat
    )
    stat.finish_timestamp = time.time()
    stat.leaf_node_counter = count_leaf_node(index_root)
    stat.solver_result = list(result_set)
    for result in result_set:
        print(result)
        print(result[0])
        print(result[1])
    result_graph_save(result_graph=[result[0] for result in result_set], dataset_path=args.input)
    statistic_file_save(stat=stat, dataset_path=args.input)
    print(stat.generate_stat_result())
