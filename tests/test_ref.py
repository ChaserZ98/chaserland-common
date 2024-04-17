from chaserland_common.ref import Ref


class TestRef:
    def setup_method(self):
        self.list_ref = Ref[list]([1, 2, 3])
        self.dict_ref = Ref[dict]({"a": 1, "b": 2, "c": 3})
        self.str_ref = Ref[str]("Hello, World!")
        self.int_ref = Ref[int](1234567890)
        self.float_ref = Ref[float](3.14159265359)

    def test_mutable_ref(self):
        assert self.list_ref.current == [1, 2, 3]
        a = self.list_ref.current
        a.append(4)
        assert self.list_ref.current == [1, 2, 3, 4]
        assert a == [1, 2, 3, 4]

        self.list_ref.current = [4, 5, 6]
        assert self.list_ref.current == [4, 5, 6]

        assert self.dict_ref.current == {"a": 1, "b": 2, "c": 3}
        a = self.dict_ref.current
        a["d"] = 4
        assert self.dict_ref.current == {"a": 1, "b": 2, "c": 3, "d": 4}
        assert a == {"a": 1, "b": 2, "c": 3, "d": 4}

        self.dict_ref.current = {"d": 4, "e": 5, "f": 6}
        assert self.dict_ref.current == {"d": 4, "e": 5, "f": 6}

    def test_immutable_ref(self):
        assert self.str_ref.current == "Hello, World!"
        a = self.str_ref.current
        a += "!!!"
        assert self.str_ref.current == "Hello, World!"
        assert a == "Hello, World!!!!"

        self.str_ref.current = "Hello, Python!"
        assert self.str_ref.current == "Hello, Python!"

        assert self.int_ref.current == 1234567890
        a = self.int_ref.current
        a += 1
        assert self.int_ref.current == 1234567890
        assert a == 1234567891

        self.int_ref.current = 9876543210
        assert self.int_ref.current == 9876543210

        assert self.float_ref.current == 3.14159265359
        a = self.float_ref.current
        a += 1.0
        assert self.float_ref.current == 3.14159265359
        assert a == 4.14159265359

        self.float_ref.current = 2.71828182846
        assert self.float_ref.current == 2.71828182846
