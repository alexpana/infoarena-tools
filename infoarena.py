#!/usr/bin/python

import os
import stat
import sys
import shutil
import subprocess

CWD = os.getcwd()


def discover_tests(test_dir):
    test_cases = []
    for f in os.listdir(test_dir):
        if f.endswith(".in"):
            input_file = os.path.join(test_dir, f)
            output_file = os.path.join(test_dir, f[:-3] + ".out")
            if os.path.exists(output_file):
                test_cases.append((input_file, output_file))
    return test_cases


def find_executable(path, problem = None):
    for f in os.listdir(path):
        if f.endswith(".exe") or (f == problem and is_executable(f)):
            return f
    return None


def is_executable(path):
    file_stat = os.stat(path)[stat.ST_MODE]
    return file_stat & stat.S_IXUSR > 0


def run_tests(problem):
    print "Running tests for", problem

    test_dir = os.path.join(CWD, "test")
    tests = discover_tests(test_dir)

    executable = find_executable(CWD, problem)

    if executable == None:
        print "Could not find the executable"
        return -1

    # copy the executable to the test directory
    test_executable = os.path.join(test_dir, executable)
    shutil.copy(os.path.join(CWD, executable), os.path.join(test_dir, executable))

    input_file = os.path.join(test_dir, problem + ".in")
    output_file = os.path.join(test_dir, problem + ".out")

    failed_tests = []

    try:
        # run each test
        for test in tests:
            shutil.copy(test[0], input_file)

            # run the solution
            subprocess.call(test_executable, cwd = test_dir)

            # compare the output
            try:
                diff_output = subprocess.check_output(["diff", "-Z", test[1], output_file], cwd = test_dir)
            except subprocess.CalledProcessError as e:
                failed_tests.append(os.path.split(test[0])[1][:-3])

            # TODO: provide meaningful diff of the output

        if len(failed_tests) > 0:
            print len(failed_tests), "out of", len(tests), "tests failed."
            print "Failed tests:", failed_tests
        elif len(tests) == 0:
            print "No tests were found"
        else:
            print "All tests passed"

    finally:
        if os.path.exists(input_file):
            os.remove(input_file)

        if os.path.exists(output_file):
            os.remove(output_file)

    return 0


def deduce_problem_from_cwd():
    return os.path.split(CWD)[1]


def create_solution(problem):
    solution_path = os.path.join(CWD, problem)

    if os.path.exists(solution_path):
        print "Solution exists."
        return

    os.mkdir(solution_path)

    write_main_source(solution_path, problem)

    write_makefile(solution_path, problem)

    os.mkdir(os.path.join(solution_path, "test"))


def write_main_source(solution_path, problem):
    source_file = open(os.path.join(solution_path, problem + ".cpp"), "w")
    source_file.write(
        "#include<fstream>\n" + 
        "using namespace std;\n" + 
        "\n" + 
        "int main() {\n" + 
        "ifstream fin(\"" + problem + ".in\");\n" +
        "ofstream fout(\"" + problem + ".out\");\n" + 
        "\n\nfin.close();\n" + 
        "fout.close();\n" + 
        "}\n")
    source_file.close()


def write_makefile(solution_path, problem):
    make_file = open(os.path.join(solution_path, "Makefile"), "w")
    make_file.write(
        "compile: " + problem + ".cpp\n" +
        "\tg++ -g -Wall -O2 " + problem + ".cpp -lm -o " + problem + "\n" +
        "\n" +
        "test: compile\n" +
        "\t@../infoarena.py test\n" +
        "\n" +
        "clean:\n" +
        "\t@rm -f " + problem + "\n" +
        "\t@rm -f test/" + problem + "\n" +
        "\t@rm -f *~ *.o\n")
    make_file.close()


def print_usage():
    print "usage: infoarena <command> [<args>]"
    print
    print "The supported commands are:"
    print "   create    creates a new solution"
    print "   test      runs the tests for the current solution (from the solution dir)"
    print


def print_usage_create():
    print "usage: infoarena create <solution_name>"


def print_usage_test():
    pass


def run():
    if len(sys.argv) < 2:
        print_usage()
        return

    cmd = sys.argv[1]

    if cmd == "create":
        if len(sys.argv) < 3:
            print_usage_create()
        else:
            solution_name = sys.argv[2]
            create_solution(solution_name)
        return

    if cmd == "test":
        problem = deduce_problem_from_cwd()
        run_tests(problem)
        return

if __name__ == "__main__":
    run()
