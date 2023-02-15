#include "doctest/doctest.h"

#include "foo.hpp"

TEST_SUITE("foo") {
  TEST_CASE("value_is_one") {
    Foo foo{1};
    CHECK_EQ(foo.get_value(), 1);
  }
}
