
#include "stdafx.h"

#include <string>

#include <Python.h>

#include "exe.h"


#if 0
int APIENTRY _tWinMain(HINSTANCE hInstance,
                     HINSTANCE hPrevInstance,
                     LPTSTR    lpCmdLine,
                     int       nCmdShow)
#else
int _tmain(int argc, _TCHAR* argv[])
#endif
{
	TCHAR szFileName[MAX_PATH];
	GetModuleFileName( NULL, szFileName, MAX_PATH );

	std::wstring executable = szFileName;
	std::wstring executable_dirname;
	std::wstring path;

	std::wstring::size_type last_delimiter_pos = executable.find_last_of( L"\\/" );
	if(last_delimiter_pos != executable.npos)
	{
		executable_dirname = executable.substr( 0, last_delimiter_pos );
	}

	path = executable_dirname + L";" +
		   executable_dirname + L"/library.zip" + L";" +
		   executable_dirname + L"/DLLs";

	//wprintf(L"%s\n",executable_dirname.c_str());

	Py_SetProgramName( const_cast<wchar_t*>(executable.c_str()) );
	Py_SetPath(path.c_str());

	Py_Initialize();

	PySys_SetArgvEx( argc, argv, 0 );

    PyObject * pName = PyUnicode_FromString( "lredit_main" );
    PyObject * pModule = PyImport_Import(pName);

    if(pModule==NULL)
	{
        PyErr_Print();
    }

	Py_XDECREF(pModule);
    Py_XDECREF(pName);

	Py_Finalize();

	return 0;
}
