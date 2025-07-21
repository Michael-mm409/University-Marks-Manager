#include <stdexcept>
#include <iostream>
#include <vector>

long long fib(int n) {
    if ( n < 0) {
        throw std::invalid_argument("Negative arguments are not allowed.");
    }

    static std::vector<long long> memo = {0, 1}; // memo[0] = 0, memo[1] = 1

    if (n < memo.size()) {
        return memo[n];
    }

    for (int i = memo.size(); i <= n; ++i) {
        memo.push_back(memo[i - 1] + memo[i - 2]);
    }

    return memo[n];
}

int main() {
    for (int index = 0; index < 100; ++index) {
        try {
            std::cout << "fib(" << index << ") = " << fib(index) << std::endl;
        } catch (const std::invalid_argument& e) {
            std::cerr << "Error: " << e.what() << std::endl;
        }
    }
}