###############################################################################
# Top contributors (to current version):
#   José Neto, Aina Niemetz
#
# This file is part of the cvc5 project.
#
# Copyright (c) 2009-2025 by the authors listed in the file AUTHORS
# in the top-level source directory and their institutional affiliations.
# All rights reserved.  See the file COPYING in the top-level source
# directory for licensing information.
# #############################################################################
#
# Generate the type checker implementation from the kinds file and the type
# checker template.
#
##
import argparse
import sys
import os
from datetime import date
from theory_validator import TheoryValidator

try:
    import tomllib
except ImportError:
    import tomli as tomllib


class CodeGenerator:

    def __init__(self, type_checker_template, type_checker_template_output,
                 input_command):
        self.typerules = ""
        self.pre_typerules = ""
        self.const_rules = ""
        self.type_checker_includes = ""
        self.template_data = ""
        self.input_command = input_command

        current_year = date.today().year
        self.copyright = f"2010-{current_year}"

        self.copyright_replacement_pattern = b'${copyright}'
        self.generation_command_replacement_pattern = b'${generation_command}'
        self.template_file_path_replacement_pattern = b'${template_file_path}'
        self.typerules_replacement_pattern = b'${typerules}'
        self.pre_typerules_replacement_pattern = b'${pretyperules}'
        self.const_rules_replacement_pattern = b'${construles}'
        self.typechecker_header_replacement_pattern = b'${typechecker_includes}'

        self.file_header = f"""/******************************************************************************
 * This file is part of the cvc5 project.
 *
 * Copyright (c) {self.copyright} by the authors listed in the file AUTHORS
 * in the top-level source directory and their institutional affiliations.
 * All rights reserved.  See the file COPYING in the top-level source
 * directory for licensing information.
 * ****************************************************************************
 *
 * This file was automatically generated by:
 *
 *     {self.input_command}
 *
 * for the cvc5 project.
 */
 
/* THIS FILE IS AUTOMATICALLY GENERATED, DO NOT EDIT ! */
/* THIS FILE IS AUTOMATICALLY GENERATED, DO NOT EDIT ! */
/* THIS FILE IS AUTOMATICALLY GENERATED, DO NOT EDIT ! */
/* THIS FILE IS AUTOMATICALLY GENERATED, DO NOT EDIT ! */
/* THIS FILE IS AUTOMATICALLY GENERATED, DO NOT EDIT ! */
/* THIS FILE IS AUTOMATICALLY GENERATED, DO NOT EDIT ! */

/* THIS FILE IS AUTOMATICALLY GENERATED, DO NOT EDIT ! */
/* THIS FILE IS AUTOMATICALLY GENERATED, DO NOT EDIT ! */
/* THIS FILE IS AUTOMATICALLY GENERATED, DO NOT EDIT ! */
/* THIS FILE IS AUTOMATICALLY GENERATED, DO NOT EDIT ! */
/* THIS FILE IS AUTOMATICALLY GENERATED, DO NOT EDIT ! */
/* THIS FILE IS AUTOMATICALLY GENERATED, DO NOT EDIT ! */

/* Edit the template file instead:                     */
/* {type_checker_template} */\n
""".encode('ascii')
        self.type_checker_template = type_checker_template
        self.type_checker_template_output = type_checker_template_output

    def read_template_data(self):
        with open(self.type_checker_template, "rb") as f:
            self.template_data = f.read()

    def generate_file_header(self):
        self.fill_template(self.template_file_path_replacement_pattern,
                           self.type_checker_template)

    def generate_code_for_typerules(self, input_kinds):
        for input_kind in input_kinds:
            if "typerule" not in input_kind:
                continue

            input_kind_type = input_kind["type"]
            input_typerule_name = input_kind[
                "K1"] if input_kind_type == 'parameterized' else input_kind[
                    "name"]
            input_typerule_type_checker_class = input_kind["typerule"]

            self.typerules = f"""{self.typerules}
    case Kind::{input_typerule_name}:
        typeNode = {input_typerule_type_checker_class}::computeType(nodeManager, n, check, errOut);
        break;
            """

            self.pre_typerules = f"""{self.pre_typerules}
    case Kind::{input_typerule_name}:
        typeNode = {input_typerule_type_checker_class}::preComputeType(nodeManager, n);
        break;
            """

    def generate_code_for_type_checker_includes(self, type_checker_include):
        self.type_checker_includes = f"{self.type_checker_includes}\n#include \"{type_checker_include}\""

    def generate_code_for_const_rules(self, input_kinds):
        for input_kind in input_kinds:
            if 'construle' not in input_kind:
                continue

            input_kind_type = input_kind["type"]
            input_const_rule_name = input_kind[
                "K1"] if input_kind_type == 'parameterized' else input_kind[
                    "name"]
            input_const_rule_checker_class = input_kind["construle"]

            self.const_rules = f"""{self.const_rules}
    case Kind::{input_const_rule_name}:
        return {input_const_rule_checker_class}::computeIsConst(nodeManager, n);
            """

    def fill_type_checker_includes_template_data(self):
        self.fill_template(self.typechecker_header_replacement_pattern,
                           self.type_checker_includes)

    def fill_typerules_template_data(self):
        self.fill_template(self.typerules_replacement_pattern, self.typerules)
        self.fill_template(self.pre_typerules_replacement_pattern,
                           self.pre_typerules)

    def fill_const_rules_template_data(self):
        self.fill_template(self.const_rules_replacement_pattern,
                           self.const_rules)

    def fill_template(self, target_pattern, replacement_string):
        self.template_data = self.template_data.replace(
            target_pattern, str.encode(replacement_string))

    def write_output_data(self):
        with open(self.type_checker_template_output, 'wb') as f:
            f.write(self.file_header)
            f.write(self.template_data)


def mkexpr_main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--kinds',
                        nargs='+',
                        help='List of input TOML files',
                        required=True,
                        type=str)
    parser.add_argument('--template',
                        help='Path to the template',
                        required=True,
                        type=str)
    parser.add_argument('--output', help='Output path', required=True)

    args = parser.parse_args()
    type_checker_template_path = args.template
    output_path = args.output
    kinds_files = args.kinds

    input_command = ' '.join(sys.argv)

    cg = CodeGenerator(type_checker_template_path, output_path, input_command)
    cg.read_template_data()
    cg.generate_file_header()

    tv = TheoryValidator()

    # Check if given kinds files exist.
    for file in kinds_files:
        if not os.path.exists(file):
            exit(f"Kinds file '{file}' does not exist")

    # Parse and check toml files
    for filename in kinds_files:
        try:
            with open(filename, "rb") as f:
                kinds_data = tomllib.load(f)
                tv.validate_theory(filename, kinds_data)

                input_kinds = kinds_data.get("kinds", [])
                cg.generate_code_for_typerules(input_kinds)

                type_checker_include = kinds_data["theory"][
                    "typechecker_header"]
                cg.generate_code_for_type_checker_includes(
                    type_checker_include)

                cg.generate_code_for_const_rules(input_kinds)
        except Exception as e:
            print(f"Could not parse file {filename}")
            print(e)
            exit(1)

    cg.fill_typerules_template_data()
    cg.fill_type_checker_includes_template_data()
    cg.fill_const_rules_template_data()
    cg.write_output_data()


if __name__ == "__main__":
    mkexpr_main()
    exit(0)
