/******************************************************************************
 * Top contributors (to current version):
 *   Aina Niemetz, Andrew Reynolds
 *
 * This file is part of the cvc5 project.
 *
 * Copyright (c) 2009-2025 by the authors listed in the file AUTHORS
 * in the top-level source directory and their institutional affiliations.
 * All rights reserved.  See the file COPYING in the top-level source
 * directory for licensing information.
 * ****************************************************************************
 *
 * Util functions for theory BV.
 */

#include "cvc5_private.h"

#ifndef CVC5__THEORY__FP__UTILS_H
#define CVC5__THEORY__FP__UTILS_H

#include "expr/type_node.h"
#include "util/integer.h"

namespace cvc5::internal {
namespace theory {
namespace fp {
namespace utils {

/**
 * Get the cardinality of the given FP type node.
 * @param type The type node.
 * @return The cardinality.
 */
Integer getCardinality(const TypeNode& type);

/**
 * Check whether the node has a type that is disallowed by --fp-exp and throw
 * an exception.
 * @param n The node to check.
 */
void checkForExperimentalFloatingPointType(const Node& n);

}  // namespace utils
}  // namespace fp
}  // namespace theory
}  // namespace cvc5::internal
#endif
