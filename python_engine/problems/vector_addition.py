import torch
import ctypes
from typing import List, Dict, Tuple, Any

from problem import Problem

class vector_addition(Problem):
    """Vector addition problem."""
    
    def __init__(self):
        super().__init__(
            name="vector-addition",
            description="Implement a CUDA kernel for vector addition: C = A + B"
        )
    
    def reference_solution(self, A: torch.Tensor, B: torch.Tensor) -> torch.Tensor:
        """
        PyTorch implementation of vector addition.
        
        Args:
            A: First input tensor
            B: Second input tensor
            
        Returns:
            Result of A + B
        """
        with torch.no_grad():
            return A + B
    
    def generate_test_cases(self) -> List[Dict[str, Any]]:
        """
        Generate test cases for vector addition.
        
        Returns:
            List of test case dictionaries with varying sizes
        """
        # Standard sizes for testing
        sizes = [
            ("1M elements", 1_000_000),
            ("5M elements", 5_000_000),
            ("10M elements", 10_000_000),
            ("50M elements", 50_000_000),
            ("100M elements", 100_000_000),
            ("1B elements", 1_000_000_000)
        ]
        
        return [
            {
                "name": name,
                "dims": (size,),
                "create_inputs": lambda size=size: (
                    torch.rand(size, device="cuda", dtype=torch.float32),
                    torch.rand(size, device="cuda", dtype=torch.float32)
                )
            }
            for name, size in sizes
        ]
    
    def verify_result(self, expected_output: torch.Tensor, 
                     actual_output: torch.Tensor) -> Tuple[bool, Dict[str, Any]]:
        """
        Verify if the vector addition result is correct.
        
        Args:
            expected_output: Output from reference solution
            actual_output: Output from submitted solution
            
        Returns:
            Tuple of (is_correct, debug_info)
        """
        is_close = torch.allclose(actual_output, expected_output, rtol=1e-5, atol=1e-5)
        
        debug_info = {}
        if not is_close:
            diff = actual_output - expected_output
            max_diff = torch.max(torch.abs(diff)).item()
            first_diff_index = torch.where(torch.abs(diff) > 1e-5)[0][0].item()
            actual_next_5_elements = [f"{x:.7f}" for x in actual_output[first_diff_index:first_diff_index+3].tolist()]
            expected_next_5_elements = [f"{x:.7f}" for x in expected_output[first_diff_index:first_diff_index+3].tolist()]
            
            debug_info = {
                "First index where output differs from expected": first_diff_index,
                "Actual values at first detected difference": actual_next_5_elements,
                "Expected values at first detected difference": expected_next_5_elements,
                "Maximum difference of any two corresponding elements": max_diff
            }
        
        return is_close, debug_info
    
    def get_function_signature(self) -> Dict[str, Any]:
        """
        Get the function signature for the vector addition solution.
        
        Returns:
            Dictionary with argtypes and restype for ctypes
        """
        return {
            "argtypes": [
                ctypes.POINTER(ctypes.c_float),  # input_a
                ctypes.POINTER(ctypes.c_float),  # input_b
                ctypes.POINTER(ctypes.c_float),  # output
                ctypes.c_size_t                  # N
            ],
            "restype": None
        }
    
    def get_flops(self, test_case: Dict[str, Any]) -> int:
        """
        Get the number of floating point operations for the problem.
        
        Args:
            test_case: The test case dictionary
            
        Returns:
            Number of floating point operations
        """
        # Vector addition has 1 FLOP per element
        N = test_case["dims"][0]
        return N
    
    def get_extra_params(self, test_case: Dict[str, Any]) -> List[Any]:
        """
        Get extra parameters to pass to the CUDA solution.
        
        Args:
            test_case: The test case dictionary
            
        Returns:
            List containing the vector length N
        """
        N = test_case["dims"][0]
        return [N]